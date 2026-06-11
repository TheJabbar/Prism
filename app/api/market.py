from fastapi import APIRouter, Query
from typing import Optional
from app.services.market_service import market_service
from app.services.cache_service import cache

router = APIRouter()


@router.get("/summary")
async def get_market_summary():
    cached = cache.get("market_summary")
    if cached:
        return cached
    data = await market_service.get_market_summary()
    cache.set("market_summary", data, ttl_seconds=30)
    return data


@router.get("/snapshots")
async def get_snapshots(symbols: Optional[str] = Query(None)):
    symbol_list = symbols.split(",") if symbols else None
    return await market_service.get_latest_snapshots(symbol_list)


@router.get("/indicators")
async def get_indicators(category: Optional[str] = None):
    return await market_service.get_indicators(category)
