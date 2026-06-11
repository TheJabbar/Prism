from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, desc
from app.database.session import async_session_factory
from app.database.models import MarketSnapshot
from app.services.cache_service import cache
from app.scrapers.market.yahoo_fetcher import fetch_all_tickers as fetch_real_tickers_all
from app.utils.logger import logger

router = APIRouter()


class TickerUpdate(BaseModel):
    symbol: str
    snapshot_type: str = "equity"
    last_price: float
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None


_SIMULATED_TICKERS = [
    {"symbol": "IHSG", "type": "index", "price": 6845.32, "change": -23.45, "change_pct": -0.34, "volume": 0},
    {"symbol": "LQ45", "type": "index", "price": 912.45, "change": -5.67, "change_pct": -0.62, "volume": 0},
    {"symbol": "USD/IDR", "type": "fx", "price": 16250.0, "change": 75.0, "change_pct": 0.46, "volume": 0},
    {"symbol": "EUR/IDR", "type": "fx", "price": 17687.0, "change": 45.0, "change_pct": 0.25, "volume": 0},
    {"symbol": "BBCA", "type": "equity", "price": 10250.0, "change": 175.0, "change_pct": 1.74, "volume": 25400000},
    {"symbol": "BBRI", "type": "equity", "price": 5850.0, "change": -85.0, "change_pct": -1.43, "volume": 42100000},
    {"symbol": "TLKM", "type": "equity", "price": 3650.0, "change": 45.0, "change_pct": 1.25, "volume": 18700000},
    {"symbol": "ASII", "type": "equity", "price": 5650.0, "change": 120.0, "change_pct": 2.17, "volume": 12300000},
    {"symbol": "BMRI", "type": "equity", "price": 6850.0, "change": -55.0, "change_pct": -0.80, "volume": 15800000},
    {"symbol": "SBN 10Y", "type": "bond", "price": 7.12, "change": 0.04, "change_pct": 0.56, "volume": 0},
    {"symbol": "DXY", "type": "index", "price": 104.50, "change": 0.25, "change_pct": 0.24, "volume": 0},
    {"symbol": "Brent", "type": "commodity", "price": 82.30, "change": 0.85, "change_pct": 1.04, "volume": 0},
    {"symbol": "CPO", "type": "commodity", "price": 3890.0, "change": -25.0, "change_pct": -0.64, "volume": 0},
    {"symbol": "Gold", "type": "commodity", "price": 2330.0, "change": 12.5, "change_pct": 0.54, "volume": 0},
]


@router.get("/")
async def list_tickers():
    cached = cache.get("tickers_list")
    if cached:
        return cached

    try:
        real = await fetch_real_tickers_all()
        if real:
            result = [
                {
                    "symbol": t["symbol"],
                    "type": t["type"],
                    "last_price": t["last_price"],
                    "change": t["change"],
                    "change_pct": t["change_pct"],
                    "volume": t["volume"],
                    "updated_at": t["timestamp"].isoformat() if t.get("timestamp") else None,
                }
                for t in real
            ]
            cache.set("tickers_list", result, ttl_seconds=60)
            return result
    except Exception as e:
        logger.warning(f"Real tickers fetch failed: {e}")

    async with async_session_factory() as session:
        try:
            subq = (
                select(MarketSnapshot.symbol, MarketSnapshot.timestamp.label("max_ts"))
                .group_by(MarketSnapshot.symbol)
                .subquery()
            )
            query = (
                select(MarketSnapshot)
                .join(subq, (MarketSnapshot.symbol == subq.c.symbol) & (MarketSnapshot.timestamp == subq.c.max_ts))
                .order_by(MarketSnapshot.symbol)
            )
            result = await session.execute(query)
            rows = result.scalars().all()
            if rows:
                output = [
                    {
                        "symbol": r.symbol,
                        "type": r.snapshot_type,
                        "last_price": r.last_price,
                        "change": r.change,
                        "change_pct": r.change_pct,
                        "volume": r.volume,
                        "updated_at": r.timestamp.isoformat() if r.timestamp else None,
                    }
                    for r in rows
                ]
                cache.set("tickers_list", output, ttl_seconds=30)
                return output
        except Exception as e:
            logger.warning(f"DB tickers query failed: {e}")

    return _convert_simulated(_SIMULATED_TICKERS)


def _convert_simulated(sim):
    return [
        {
            "symbol": t["symbol"],
            "type": t["type"],
            "last_price": t["price"],
            "change": t["change"],
            "change_pct": t["change_pct"],
            "volume": t["volume"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        for t in sim
    ]


@router.get("/{symbol}")
async def get_ticker(symbol: str):
    try:
        from app.scrapers.market.yahoo_fetcher import fetch_ticker_data as fetch_single
        real = await fetch_single(symbol.upper())
        if real:
            return {
                "symbol": real["symbol"],
                "last_price": real["last_price"],
                "change": real["change"],
                "change_pct": real["change_pct"],
                "volume": real["volume"],
                "updated_at": real["timestamp"].isoformat() if real.get("timestamp") else None,
            }
    except Exception as e:
        logger.warning(f"Real single ticker fetch failed: {e}")

    async with async_session_factory() as session:
        try:
            query = (
                select(MarketSnapshot)
                .where(MarketSnapshot.symbol == symbol.upper())
                .order_by(desc(MarketSnapshot.timestamp))
                .limit(1)
            )
            result = await session.execute(query)
            row = result.scalar_one_or_none()
            if row:
                return {
                    "symbol": row.symbol,
                    "last_price": row.last_price,
                    "change": row.change,
                    "change_pct": row.change_pct,
                    "volume": row.volume,
                    "updated_at": row.timestamp.isoformat() if row.timestamp else None,
                }
        except Exception as e:
            logger.warning(f"DB ticker query failed: {e}")

    for t in _SIMULATED_TICKERS:
        if t["symbol"].upper() == symbol.upper():
            return {
                "symbol": t["symbol"],
                "last_price": t["price"],
                "change": t["change"],
                "change_pct": t["change_pct"],
                "volume": t["volume"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

    raise HTTPException(status_code=404, detail=f"Ticker '{symbol.upper()}' not found")


@router.post("/")
async def upsert_ticker(data: TickerUpdate):
    async with async_session_factory() as session:
        snap = MarketSnapshot(
            symbol=data.symbol.upper(),
            snapshot_type=data.snapshot_type,
            last_price=data.last_price,
            change=data.change,
            change_pct=data.change_pct,
            volume=data.volume or 0,
            timestamp=datetime.now(timezone.utc),
        )
        session.add(snap)
        await session.commit()
        cache.invalidate("tickers_list")
        cache.invalidate("market_summary")
        return {
            "status": "updated",
            "symbol": snap.symbol,
            "last_price": snap.last_price,
            "timestamp": snap.timestamp.isoformat(),
        }


@router.delete("/{symbol}")
async def delete_ticker(symbol: str):
    async with async_session_factory() as session:
        try:
            query = select(MarketSnapshot).where(MarketSnapshot.symbol == symbol.upper())
            result = await session.execute(query)
            rows = result.scalars().all()
            if not rows:
                raise HTTPException(status_code=404, detail=f"Ticker '{symbol.upper()}' not found")
            for row in rows:
                await session.delete(row)
            await session.commit()
            cache.invalidate("tickers_list")
            cache.invalidate("market_summary")
            return {"status": "deleted", "symbol": symbol.upper()}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed")
async def seed_tickers():
    async with async_session_factory() as session:
        try:
            created = []
            for t in _SIMULATED_TICKERS:
                snap = MarketSnapshot(
                    symbol=t["symbol"],
                    snapshot_type=t["type"],
                    last_price=t["price"],
                    change=t["change"],
                    change_pct=t["change_pct"],
                    volume=t["volume"],
                    timestamp=datetime.now(timezone.utc),
                )
                session.add(snap)
                created.append(t)
            await session.commit()
            cache.invalidate("tickers_list")
            cache.invalidate("market_summary")
            return {"status": "ok", "count": len(created), "tickers": [r["symbol"] for r in created]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_tickers():
    real = await fetch_real_tickers_all()
    if real:
        async with async_session_factory() as session:
            for t in real:
                snap = MarketSnapshot(
                    symbol=t["symbol"],
                    snapshot_type=t["type"],
                    last_price=t["last_price"],
                    change=t["change"],
                    change_pct=t["change_pct"],
                    volume=t["volume"],
                    timestamp=datetime.now(timezone.utc),
                )
                session.add(snap)
            await session.commit()
        cache.invalidate("tickers_list")
        cache.invalidate("market_summary")
        return {
            "status": "refreshed",
            "count": len(real),
            "tickers": [t["symbol"] for t in real],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {"status": "error", "message": "Could not fetch real data"}
