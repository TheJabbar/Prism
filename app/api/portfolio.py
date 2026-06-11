from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.database.session import async_session_factory
from app.database.models import Portfolio, Holding

router = APIRouter()


class PortfolioCreate(BaseModel):
    name: str


class HoldingCreate(BaseModel):
    portfolio_id: int
    ticker: str
    quantity: float
    avg_price: float
    currency: str = "IDR"
    opened_at: Optional[str] = None


@router.get("/")
async def list_portfolios():
    async with async_session_factory() as session:
        from sqlalchemy import select
        result = await session.execute(select(Portfolio))
        portfolios = result.scalars().all()
        return [
            {"id": p.id, "name": p.name, "created_at": p.created_at.isoformat() if p.created_at else None}
            for p in portfolios
        ]


@router.get("/demo")
async def get_demo_portfolio():
    return {
        "portfolio": {
            "id": 1,
            "name": "Demo Portfolio",
            "total_value": 125000000,
            "total_cost": 100000000,
            "total_pnl": 25000000,
            "total_pnl_pct": 25.0,
        },
        "holdings": [
            {"ticker": "BBCA", "name": "Bank Central Asia", "quantity": 1000, "avg_price": 9500, "last_price": 10250, "pnl_pct": 7.89, "weight": 8.2},
            {"ticker": "BBRI", "name": "Bank Rakyat Indonesia", "quantity": 2000, "avg_price": 5400, "last_price": 5850, "pnl_pct": 8.33, "weight": 9.36},
            {"ticker": "TLKM", "name": "Telkom Indonesia", "quantity": 1500, "avg_price": 3800, "last_price": 3650, "pnl_pct": -3.95, "weight": 4.38},
            {"ticker": "ASII", "name": "Astra International", "quantity": 500, "avg_price": 5200, "last_price": 5650, "pnl_pct": 8.65, "weight": 2.26},
            {"ticker": "BMRI", "name": "Bank Mandiri", "quantity": 1000, "avg_price": 6200, "last_price": 6850, "pnl_pct": 10.48, "weight": 5.48},
        ],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/")
async def create_portfolio(data: PortfolioCreate):
    async with async_session_factory() as session:
        portfolio = Portfolio(name=data.name)
        session.add(portfolio)
        await session.commit()
        return {"id": portfolio.id, "name": portfolio.name}


@router.post("/holdings")
async def add_holding(data: HoldingCreate):
    async with async_session_factory() as session:
        holding = Holding(
            portfolio_id=data.portfolio_id,
            ticker=data.ticker,
            quantity=data.quantity,
            avg_price=data.avg_price,
            currency=data.currency,
            opened_at=datetime.fromisoformat(data.opened_at) if data.opened_at else None,
        )
        session.add(holding)
        await session.commit()
        return {"id": holding.id, "ticker": holding.ticker}
