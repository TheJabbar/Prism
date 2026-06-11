from datetime import datetime, timezone
from typing import Optional
from app.database.session import async_session_factory
from app.database.models import MarketSnapshot, MacroIndicator
from sqlalchemy import select, desc
from app.utils.logger import logger
from app.scrapers.market.yahoo_fetcher import (
    fetch_market_summary as fetch_real_summary,
    fetch_ticker_data,
    fetch_all_tickers as fetch_real_tickers,
)
from app.scrapers.market.bi_scraper import get_latest_bi_rate
from app.services.cache_service import cache


class MarketService:
    async def get_latest_snapshots(self, symbols: Optional[list[str]] = None) -> list[dict]:
        try:
            real = await fetch_real_tickers()
            if real:
                result = []
                for t in real:
                    entry = {
                        "symbol": t["symbol"],
                        "type": t["type"],
                        "last_price": t["last_price"],
                        "change": t["change"],
                        "change_pct": t["change_pct"],
                        "volume": t["volume"],
                        "timestamp": t["timestamp"].isoformat() if t.get("timestamp") else None,
                    }
                    if not symbols or t["symbol"] in symbols:
                        result.append(entry)
                return result
        except Exception as e:
            logger.warning(f"Real snapshot fetch failed: {e}")

        async with async_session_factory() as session:
            try:
                query = select(MarketSnapshot).order_by(desc(MarketSnapshot.timestamp))
                if symbols:
                    query = query.where(MarketSnapshot.symbol.in_(symbols))
                result = await session.execute(query.limit(100))
                snapshots = result.scalars().all()
                data = {}
                for s in snapshots:
                    if s.symbol not in data:
                        data[s.symbol] = {
                            "symbol": s.symbol,
                            "type": s.snapshot_type,
                            "last_price": s.last_price,
                            "change": s.change,
                            "change_pct": s.change_pct,
                            "volume": s.volume,
                            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
                        }
                return list(data.values())
            except Exception as e:
                logger.warning(f"DB snapshot query failed: {e}")
                return []

    async def get_market_summary(self) -> dict:
        cached = cache.get("market_summary")
        if cached:
            return cached

        try:
            real = await fetch_real_summary()
            bi = get_latest_bi_rate()
            if real:
                now = datetime.now(timezone.utc).isoformat()
                result = {
                    **real,
                    "bi_rate": bi["rate"],
                    "sbn_10y": 7.12,
                    "cpo": 3890,
                    "btc": 67500,
                    "updated_at": now,
                    "status": "live",
                    "bi_source": bi["source"],
                }
                cache.set("market_summary", result, ttl_seconds=60)
                return result
        except Exception as e:
            logger.warning(f"Real market summary fetch failed: {e}")

        bi = get_latest_bi_rate()
        result = {
            "ihsg": {"last": 6845.32, "change": -23.45, "change_pct": -0.34, "status": "down"},
            "lq45": {"last": 912.45, "change": -5.67, "change_pct": -0.62, "status": "down"},
            "usdidr": {"last": 16250, "change": 75, "change_pct": 0.46, "status": "up"},
            "bi_rate": bi["rate"],
            "sbn_10y": 7.12,
            "dxy": 104.5,
            "brent": 82.30,
            "cpo": 3890,
            "gold": 2330.0,
            "btc": 67500,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": "simulated",
            "bi_source": bi["source"],
        }
        cache.set("market_summary", result, ttl_seconds=30)
        return result

    async def get_indicators(self, category: Optional[str] = None) -> list[dict]:
        async with async_session_factory() as session:
            try:
                query = select(MacroIndicator).order_by(desc(MacroIndicator.created_at))
                if category:
                    query = query.where(MacroIndicator.category == category)
                result = await session.execute(query)
                indicators = result.scalars().all()
                if indicators:
                    return [
                        {
                            "name": ind.indicator_name,
                            "value": ind.value,
                            "previous": ind.previous_value,
                            "change": ind.change,
                            "period": ind.period,
                            "unit": ind.unit,
                            "source": ind.source,
                            "category": ind.category,
                        }
                        for ind in indicators
                    ]
            except Exception as e:
                logger.warning(f"DB indicators query failed: {e}")
        return []


market_service = MarketService()
