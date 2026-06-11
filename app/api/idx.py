from fastapi import APIRouter, Query
from app.services.idx_service import idx_service

router = APIRouter()


@router.get("/overview")
async def idx_overview():
    return await idx_service.get_overview()


@router.get("/indices")
async def idx_indices():
    return await idx_service.get_indices()


@router.get("/indices/{code}/chart")
async def idx_index_chart(code: str, period: str = Query("1M", regex="^(1D|1W|1M|1Q|1Y)$")):
    return await idx_service.get_index_chart(code, period)


@router.get("/trade-summary")
async def idx_trade_summary():
    return await idx_service.get_trade_summary()


@router.get("/top-gainers")
async def idx_top_gainers():
    return await idx_service.get_top_gainers()


@router.get("/top-losers")
async def idx_top_losers():
    return await idx_service.get_top_losers()


@router.get("/stocks")
async def idx_stock_summary(date: str | None = None):
    return await idx_service.get_stock_summary(date)


@router.get("/stocks/{code}")
async def idx_trading_info(code: str):
    return await idx_service.get_trading_info(code)


@router.get("/screener")
async def idx_screener(sector: str = "", sub_sector: str = ""):
    return await idx_service.get_stock_screener(sector, sub_sector)


@router.get("/financial-ratios")
async def idx_financial_ratios(year: int | None = None, month: int | None = None):
    return await idx_service.get_financial_ratios(year, month)


@router.get("/companies")
async def idx_companies(start: int = 0, length: int = 100):
    return await idx_service.get_company_profiles(start, length)


@router.get("/companies/{code}")
async def idx_company_detail(code: str):
    return await idx_service.get_company_detail(code)
