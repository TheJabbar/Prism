import hashlib
from datetime import datetime, timezone
from typing import Optional
from app.utils.logger import logger

_INDONESIAN_TICKERS = {
    "BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR", "ADRO", "BYAN",
    "GOTO", "CPIN", "ICBP", "INDF", "ANTM", "ITMG", "PTBA", "PGAS",
    "SMGR", "EXCL", "ISAT", "MNCN", "JPFA", "LSIP", "BUKA", "BBNI",
    "ARTO", "BRIS", "AMRT", "ACES", "MDKA", "HRUM", "TINS", "INCO",
    "IHSG", "LQ45", "IDX30",
}


def _extract_tickers(text: str) -> list[str]:
    found = set()
    for w in text.upper().split():
        wc = w.strip("(),.:;!?\"'")
        if wc in _INDONESIAN_TICKERS:
            found.add(wc)
    return sorted(found)


_BOND_LABELS = {"sbn", "sun", "obligasi", "fr", "sukuk"}
_MACRO_LABELS = {"inflasi", "gdp", "bi rate", "suku bunga", "cadangan devisa", "neraca dagang", "ihsg", "rupiah"}
_SECTOR_LABELS = {"perbankan", "teknologi", "energi", "tambang", "properti", "konsumsi", "infrastruktur"}


def _extract_tags(title: Optional[str], summary: Optional[str]) -> list[str]:
    text = ((title or "") + " " + (summary or "")).lower()
    tags = []
    if any(w in text for w in _BOND_LABELS):
        tags.append("Bonds")
    if any(w in text for w in _MACRO_LABELS):
        tags.append("Macro")
    for word in _SECTOR_LABELS:
        if word in text:
            tags.append(word.capitalize())
    if "digital" in text or "fintech" in text:
        tags.append("Digital")
    if not tags:
        tags.append("Market")
    return tags[:5]


def _make_id(title: str) -> str:
    return hashlib.sha256(title.encode()).hexdigest()[:16]


def _parse_relative_time(text: str) -> datetime:
    now = datetime.now(timezone.utc)
    text = text.lower().strip()
    if "menit" in text or "minute" in text:
        try:
            n = int(''.join(filter(str.isdigit, text.split("menit")[0] if "menit" in text else text.split("minute")[0])))
            return now.replace(second=0, microsecond=0) - __import__('datetime').timedelta(minutes=n)
        except Exception:
            pass
    if "jam" in text or "hour" in text:
        try:
            n = int(''.join(filter(str.isdigit, text.split("jam")[0] if "jam" in text else text.split("hour")[0])))
            return now.replace(second=0, microsecond=0) - __import__('datetime').timedelta(hours=n)
        except Exception:
            pass
    if "hari" in text or "day" in text:
        try:
            n = int(''.join(filter(str.isdigit, text.split("hari")[0] if "hari" in text else text.split("day")[0])))
            return now.replace(second=0, microsecond=0) - __import__('datetime').timedelta(days=n)
        except Exception:
            pass
    return now


def _parse_article(el, source_url: str) -> Optional[dict]:
    title = el.css('h2::text').get()
    if not title:
        title = el.css('a::text').get()
    if not title:
        return None
    title = title.strip()
    if len(title) < 10:
        return None
    link = el.css('a::attr(href)').get()
    if link and not link.startswith("http"):
        from urllib.parse import urljoin
        link = urljoin(source_url, link)
    source = "CNBC Indonesia" if "cnbcindonesia" in source_url else \
             "Kontan" if "kontan" in source_url else \
             "Bisnis Indonesia" if "bisnis" in source_url else "Unknown"
    tid = _make_id(title)
    tickers = _extract_tickers(title)
    tags = _extract_tags(title, None)
    return {
        "id": tid, "title": title, "summary": title[:200],
        "url": link or f"https://example.com/{tid}",
        "source": source, "published_at": datetime.now(timezone.utc),
        "language": "id", "sentiment": None, "is_breaking": False,
        "ticker_mentions": tickers, "tags": tags,
    }


async def scrape_cnbc() -> list[dict]:
    try:
        from scrapling.fetchers import Fetcher
    except ImportError:
        logger.warning("scrapling not installed")
        return []
    url = "https://www.cnbcindonesia.com/news"
    try:
        page = Fetcher.get(url, timeout=15)
        if not page or page.status != 200:
            logger.warning(f"CNBC returned {page.status if page else 'None'}")
            return []
    except Exception as e:
        logger.warning(f"CNBC fetch failed: {e}")
        return []
    articles = []
    seen = set()
    for art in page.css("article"):
        parsed = _parse_article(art, url)
        if parsed and parsed["id"] not in seen:
            # Try to extract time from relative time elements
            time_el = art.css("span.text-xs.text-gray::text").get() or \
                      art.css("span.inline-block.font-semibold::text").get()
            if time_el:
                parsed["published_at"] = _parse_relative_time(time_el.strip())
            seen.add(parsed["id"])
            articles.append(parsed)
    logger.info(f"CNBC: {len(articles)} articles")
    return articles


async def scrape_kontan() -> list[dict]:
    try:
        from scrapling.fetchers import Fetcher
    except ImportError:
        return []
    url = "https://www.kontan.co.id/"
    try:
        page = Fetcher.get(url, timeout=15)
        if not page or page.status != 200:
            return []
    except Exception as e:
        logger.warning(f"Kontan fetch failed: {e}")
        return []
    articles = []
    seen = set()
    for div in page.css("div.list-berita"):
        for li in div.css("li"):
            a = li.css("a")
            if not a:
                continue
            href = a.css("::attr(href)").get()
            texts = [t.strip() for t in li.css("::text").getall() if t.strip()]
            title = None
            time_text = None
            for t in texts:
                if "|" in t:
                    parts = [p.strip() for p in t.split("|")]
                    for p in parts:
                        if "menit" in p or "jam" in p or "hari" in p:
                            time_text = p
            # Title is usually the longest text or the one without | or time words
            non_time_texts = [t for t in texts if "menit" not in t and "jam" not in t and "hari" not in t and t != "|"]
            if non_time_texts:
                title = max(non_time_texts, key=len)
            if not title or len(title) < 10:
                continue
            idx = texts.index(title)
            category = texts[idx - 2] if idx >= 2 and texts[idx - 1] == "|" else ""
            tid = _make_id(title)
            if tid not in seen:
                seen.add(tid)
                articles.append({
                    "id": tid, "title": title, "summary": title[:200],
                    "url": href or f"https://example.com/{tid}",
                    "source": "Kontan", "published_at": _parse_relative_time(time_text) if time_text else datetime.now(timezone.utc),
                    "language": "id", "sentiment": None, "is_breaking": False,
                    "ticker_mentions": _extract_tickers(title), "tags": _extract_tags(title, None),
                })
    logger.info(f"Kontan: {len(articles)} articles")
    return articles


async def scrape_bisnis() -> list[dict]:
    try:
        from scrapling.fetchers import Fetcher
    except ImportError:
        return []
    url = "https://www.bisnis.com/"
    try:
        page = Fetcher.get(url, timeout=15)
        if not page or page.status != 200:
            return []
    except Exception as e:
        logger.warning(f"Bisnis fetch failed: {e}")
        return []
    articles = []
    seen = set()
    for a in page.css("a[href*=read]"):
        href = a.css("::attr(href)").get()
        title = a.css("::text").get()
        if not title or len(title.strip()) < 10:
            continue
        title = title.strip()
        tid = _make_id(title)
        if tid not in seen:
            seen.add(tid)
            articles.append({
                "id": tid, "title": title, "summary": title[:200],
                "url": href or f"https://example.com/{tid}",
                "source": "Bisnis Indonesia", "published_at": datetime.now(timezone.utc),
                "language": "id", "sentiment": None, "is_breaking": False,
                "ticker_mentions": _extract_tickers(title), "tags": _extract_tags(title, None),
            })
    logger.info(f"Bisnis: {len(articles)} articles")
    return articles


async def scrape_all_news() -> list[dict]:
    all_articles = []
    for scraper in [scrape_cnbc, scrape_kontan, scrape_bisnis]:
        try:
            all_articles.extend(await scraper())
        except Exception as e:
            logger.warning(f"News scraper failed: {e}")
    all_articles.sort(key=lambda a: a.get("published_at") or datetime.min, reverse=True)
    seen = set()
    unique = []
    for a in all_articles:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    logger.info(f"Total scraped: {len(unique)} unique articles")
    return unique
