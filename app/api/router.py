from fastapi import APIRouter
from app.api.market import router as market_router
from app.api.news import router as news_router
from app.api.indicators import router as indicators_router
from app.api.bonds import router as bonds_router
from app.api.fx import router as fx_router
from app.api.portfolio import router as portfolio_router
from app.api.ai_analyst import router as ai_router
from app.api.alerts import router as alerts_router
from app.api.export import router as export_router
from app.api.tickers import router as tickers_router
from app.api.idx import router as idx_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(tickers_router, prefix="/tickers", tags=["Tickers"])
api_router.include_router(market_router, prefix="/market", tags=["Market"])
api_router.include_router(news_router, prefix="/news", tags=["News"])
api_router.include_router(indicators_router, prefix="/indicators", tags=["Indicators"])
api_router.include_router(bonds_router, prefix="/bonds", tags=["Bonds"])
api_router.include_router(fx_router, prefix="/fx", tags=["FX"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Analyst"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(export_router, prefix="/export", tags=["Export"])
api_router.include_router(idx_router, prefix="/idx", tags=["IDX"])
