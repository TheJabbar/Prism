from datetime import datetime, timezone, timedelta
from typing import Optional
from app.database.session import async_session_factory
from app.database.models import NewsArticle, NewsSentimentSnapshot
from sqlalchemy import select, desc, func
import hashlib
import json
from app.utils.logger import logger
from app.scrapers.news.cnbc_scraper import scrape_all_news
from app.services.llm_service import llm_service


class NewsService:
    async def _llm_classify_sentiment(self, articles: list[tuple]) -> None:
        titles = [(a.id, a.title, a.summary) for a in articles if a.sentiment is None]
        if not titles:
            return
        batch_size = 20
        for i in range(0, len(titles), batch_size):
            batch = titles[i:i + batch_size]
            prompt_lines = "\n".join(
                f'{idx+1}. "{t}"' for idx, (_, t, _) in enumerate(batch)
            )
            prompt = (
                "You are a financial news sentiment classifier. "
                "For each headline below, classify the sentiment from the perspective of "
                "an Indonesian stock market investor.\n"
                "Rules:\n"
                "- Fuel/commodity price hikes, rate hikes, inflation, corruption, natural disasters → negative\n"
                "- Market rallies, GDP growth, corporate profits, rate cuts, foreign inflows → positive\n"
                "- Neutral/ambiguous news (company announcements, policy changes without clear impact) → 0.0\n"
                f"Respond with ONLY a valid JSON array of floats between -1.0 and 1.0.\n\n"
                f"Headlines:\n{prompt_lines}"
            )
            try:
                content = await llm_service.chat_completion(
                    [{"role": "user", "content": prompt}],
                    temperature=0.1, max_tokens=512,
                )
                scores = json.loads(content.strip())
                if not isinstance(scores, list) or len(scores) != len(batch):
                    raise ValueError(f"Expected {len(batch)} scores, got {scores}")
                scores = [max(-1.0, min(1.0, float(s))) for s in scores]
                async with async_session_factory() as session:
                    for (aid, _, _), score in zip(batch, scores):
                        row = await session.get(NewsArticle, aid)
                        if row:
                            row.sentiment = score
                    await session.commit()
                logger.info(f"LLM classified {len(batch)} headlines")
            except Exception as e:
                logger.warning(f"LLM sentiment batch failed: {e}")

    async def get_news(
        self,
        source: Optional[str] = None,
        language: Optional[str] = None,
        ticker: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        try:
            async with async_session_factory() as session:
                query = select(NewsArticle).order_by(desc(NewsArticle.published_at))
                if source:
                    query = query.where(NewsArticle.source.ilike(f"%{source}%"))
                if language:
                    query = query.where(NewsArticle.language == language)
                if ticker:
                    query = query.where(NewsArticle.ticker_mentions.contains(ticker))
                result = await session.execute(query.offset(offset).limit(limit))
                articles = result.scalars().all()
                if articles:
                    needs_llm = [a for a in articles if a.sentiment is None]
                    if needs_llm:
                        await self._llm_classify_sentiment(needs_llm)
                        for a in needs_llm:
                            await session.refresh(a)

                    out = []
                    for a in articles:
                        sentiment = a.sentiment if a.sentiment is not None else 0.0
                        out.append(
                            {
                                "id": a.id,
                                "title": a.title,
                                "summary": a.summary,
                                "url": a.url,
                                "source": a.source,
                                "published_at": a.published_at.isoformat() if a.published_at else None,
                                "language": a.language,
                                "sentiment": sentiment,
                                "is_breaking": a.is_breaking,
                                "ticker_mentions": a.ticker_mentions or [],
                                "tags": a.tags or [],
                            }
                        )
                    return out
        except Exception as e:
            logger.warning(f"DB query failed in get_news: {e}")

        return []

    async def get_news_sentiment(self) -> dict:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        articles = await self.get_news(limit=200)
        total = len(articles)
        if total == 0:
            return {"total": 0, "positive": 0, "neutral": 0, "negative": 0, "score": 0.0}

        pos = sum(1 for a in articles if a["sentiment"] > 0.1)
        neg = sum(1 for a in articles if a["sentiment"] < -0.1)
        neu = total - pos - neg

        result = {
            "date": today,
            "total": total,
            "positive": pos,
            "neutral": neu,
            "negative": neg,
            "pct_positive": round(pos / total * 100, 1),
            "pct_neutral": round(neu / total * 100, 1),
            "pct_negative": round(neg / total * 100, 1),
            "score": round((pos - neg) / total, 3),
        }

        try:
            async with async_session_factory() as session:
                existing = await session.execute(
                    select(NewsSentimentSnapshot).where(NewsSentimentSnapshot.date == today)
                )
                snap = existing.scalar_one_or_none()
                if snap:
                    snap.total = total
                    snap.positive = pos
                    snap.neutral = neu
                    snap.negative = neg
                    snap.pct_positive = result["pct_positive"]
                    snap.pct_neutral = result["pct_neutral"]
                    snap.pct_negative = result["pct_negative"]
                    snap.score = result["score"]
                else:
                    session.add(NewsSentimentSnapshot(
                        date=today, total=total, positive=pos, neutral=neu,
                        negative=neg, pct_positive=result["pct_positive"],
                        pct_neutral=result["pct_neutral"],
                        pct_negative=result["pct_negative"],
                        score=result["score"],
                    ))
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist sentiment snapshot: {e}")

        return result

    async def get_sentiment_history(self, days: int = 30) -> list[dict]:
        try:
            async with async_session_factory() as session:
                query = (
                    select(NewsSentimentSnapshot)
                    .order_by(desc(NewsSentimentSnapshot.date))
                    .limit(days)
                )
                result = await session.execute(query)
                snaps = result.scalars().all()
                return [
                    {
                        "date": s.date,
                        "score": s.score,
                        "positive": s.positive,
                        "neutral": s.neutral,
                        "negative": s.negative,
                        "total": s.total,
                        "pct_positive": s.pct_positive,
                        "pct_neutral": s.pct_neutral,
                        "pct_negative": s.pct_negative,
                    }
                    for s in reversed(snaps)
                ]
        except Exception as e:
            logger.warning(f"Failed to fetch sentiment history: {e}")
            return []

    async def get_breaking_news(self) -> list[dict]:
        thirty_min_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
        try:
            async with async_session_factory() as session:
                query = (
                    select(NewsArticle)
                    .where(NewsArticle.is_breaking == True)
                    .where(NewsArticle.published_at >= thirty_min_ago)
                    .order_by(desc(NewsArticle.published_at))
                    .limit(10)
                )
                result = await session.execute(query)
                articles = result.scalars().all()
                if articles:
                    return [
                        {
                            "id": a.id,
                            "title": a.title,
                            "source": a.source,
                            "published_at": a.published_at.isoformat() if a.published_at else None,
                            "sentiment": a.sentiment,
                        }
                        for a in articles
                    ]
        except Exception as e:
            logger.warning(f"DB query failed in get_breaking_news: {e}")
        return []

    async def seed_scraped_news(self):
        articles = await scrape_all_news()
        if not articles:
            logger.info("No articles scraped, using sample data")
            await self.seed_sample_news()
            return
        try:
            async with async_session_factory() as session:
                count = 0
                for art in articles:
                    existing = await session.get(NewsArticle, art["id"])
                    if not existing:
                        article = NewsArticle(
                            id=art["id"],
                            title=art["title"],
                            summary=art.get("summary"),
                            url=art.get("url"),
                            source=art.get("source"),
                            published_at=art.get("published_at"),
                            language=art.get("language", "id"),
                            sentiment=art.get("sentiment"),
                            is_breaking=art.get("is_breaking", False),
                            ticker_mentions=art.get("ticker_mentions", []),
                            tags=art.get("tags", []),
                        )
                        session.add(article)
                        count += 1
                await session.commit()
                logger.info(f"Seeded {count} scraped news articles")
        except Exception as e:
            logger.warning(f"Failed to seed scraped news: {e}")
            await self.seed_sample_news()

    async def seed_sample_news(self):
        sample_articles = [
            {
                "title": "IHSG Menguat di Tengah Sentimen Positif Data Inflasi AS",
                "summary": "Indeks Harga Saham Gabungan (IHSG) ditutup menguat pada perdagangan hari ini, didorong oleh sentimen positif dari data inflasi Amerika Serikat yang lebih rendah dari perkiraan.",
                "source": "Kontan",
                "language": "id",
                "sentiment": 0.45,
                "ticker_mentions": ["BBCA", "BBRI", "TLKM"],
                "tags": ["IHSG", "Inflasi", "AS"],
            },
            {
                "title": "BI Pertahankan Suku Bunga Acuan di 6,0%",
                "summary": "Bank Indonesia memutuskan untuk mempertahankan BI-7DRR di level 6,0% dalam RDG bulan ini, sejalan dengan upaya menjaga stabilitas rupiah.",
                "source": "Bisnis Indonesia",
                "language": "id",
                "sentiment": 0.1,
                "ticker_mentions": [],
                "tags": ["BI Rate", "BI", "Moneter"],
            },
            {
                "title": "Rupiah Melemah ke Rp16.250 per Dolar AS",
                "summary": "Nilai tukar rupiah terhadap dolar Amerika Serikat ditutup melemah di tengah kuatnya indeks dolar dan ketidakpastian global.",
                "source": "CNBC Indonesia",
                "language": "id",
                "sentiment": -0.3,
                "ticker_mentions": [],
                "tags": ["Rupiah", "USD/IDR", "DXY"],
            },
            {
                "title": "Bank Indonesia Reports Growing Digital Transaction Volume",
                "summary": "Bank Indonesia reported a significant increase in digital transaction volume, driven by the acceleration of digital banking adoption across the archipelago.",
                "source": "Jakarta Post",
                "language": "en",
                "sentiment": 0.25,
                "ticker_mentions": ["BBRI", "BMRI"],
                "tags": ["BI", "Digital Banking"],
            },
            {
                "title": "SBN Yield Turun, Permintaan Obligasi Pemerintah Meningkat",
                "summary": "Imbal hasil Surat Berharga Negara (SBN) tenor 10 tahun turun seiring meningkatnya permintaan investor asing di lelang SUN pekan ini.",
                "source": "Detik Finance",
                "language": "id",
                "sentiment": 0.35,
                "ticker_mentions": [],
                "tags": ["SBN", "SUN", "Obligasi"],
            },
        ]
        try:
            async with async_session_factory() as session:
                for art in sample_articles:
                    article_id = hashlib.sha256(art["title"].encode()).hexdigest()[:16]
                    existing = await session.get(NewsArticle, article_id)
                    if not existing:
                        article = NewsArticle(
                            id=article_id,
                            title=art["title"],
                            summary=art["summary"],
                            url=f"https://example.com/news/{article_id}",
                            source=art["source"],
                            published_at=datetime.now(timezone.utc),
                            language=art["language"],
                            sentiment=art["sentiment"],
                            is_breaking=False,
                            ticker_mentions=art["ticker_mentions"],
                            tags=art["tags"],
                        )
                        session.add(article)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to seed sample news: {e}")


news_service = NewsService()
