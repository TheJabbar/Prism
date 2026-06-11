from fastapi import APIRouter
from datetime import datetime, timezone
from typing import Optional
from app.utils.logger import logger

router = APIRouter()

_SIMULATED_YIELD_CURVE = {
    "tenors": ["2Y", "5Y", "10Y", "15Y", "20Y", "30Y"],
    "yields": [6.12, 6.55, 7.12, 7.35, 7.50, 7.65],
    "previous_yields": [6.08, 6.50, 7.08, 7.30, 7.45, 7.60],
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "status": "simulated",
}

_SIMULATED_BENCHMARKS = {
    "bonds": [
        {"isin": "IDG000010101", "name": "FR0100", "tenor": "10Y", "coupon": 6.50, "ytm": 7.12, "price": 98.50, "change": -0.15, "volume": 4500},
        {"isin": "IDG000009909", "name": "FR0099", "tenor": "5Y", "coupon": 6.00, "ytm": 6.55, "price": 99.25, "change": 0.05, "volume": 3200},
        {"isin": "IDG000009808", "name": "FR0098", "tenor": "15Y", "coupon": 7.00, "ytm": 7.35, "price": 97.80, "change": -0.25, "volume": 2800},
        {"isin": "IDG000009707", "name": "FR0097", "tenor": "20Y", "coupon": 7.25, "ytm": 7.50, "price": 97.20, "change": -0.30, "volume": 2100},
    ],
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

_SIMULATED_CDS = {
    "indonesia_5y": 72.5,
    "change": 1.2,
    "comparison": [
        {"country": "Philippines", "cds": 85.0},
        {"country": "Malaysia", "cds": 45.0},
        {"country": "Thailand", "cds": 55.0},
    ],
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

_SIMULATED_AUCTIONS = {
    "upcoming": [
        {"date": "2025-07-15", "tenor": "10Y", "target": "20 trillion", "type": "SUN Auction"},
        {"date": "2025-07-22", "tenor": "5Y", "target": "15 trillion", "type": "SUN Auction"},
    ],
    "historical": [
        {"date": "2025-06-24", "tenor": "10Y", "target": "20T", "incoming": "48.2T", "bid_to_cover": 2.41, "avg_yield": 7.15},
        {"date": "2025-06-10", "tenor": "5Y", "target": "15T", "incoming": "35.6T", "bid_to_cover": 2.37, "avg_yield": 6.58},
    ],
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


async def _fetch_real_yield_curve() -> Optional[dict]:
    try:
        import yfinance as yf
        import asyncio
        tickers = {
            "ID2Y=RR": "2Y",
            "ID5Y=RR": "5Y",
            "ID10Y=RR": "10Y",
            "ID15Y=RR": "15Y",
            "ID20Y=RR": "20Y",
            "ID30Y=RR": "30Y",
        }
        yields = []
        prev_yields = []
        tenors = []
        for sym, tenor in tickers.items():
            try:
                t = await asyncio.to_thread(yf.Ticker, sym)
                info = await asyncio.to_thread(lambda: t.info)
                if info:
                    y = info.get("regularMarketPrice") or info.get("previousClose")
                    py = info.get("regularMarketPreviousClose") or y
                    if y:
                        tenors.append(tenor)
                        yields.append(round(float(y), 2))
                        prev_yields.append(round(float(py) if py else float(y), 2))
            except Exception:
                continue
        if tenors:
            return {
                "tenors": tenors,
                "yields": yields,
                "previous_yields": prev_yields,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "live",
            }
    except Exception as e:
        logger.warning(f"Failed to fetch real yield curve: {e}")
    return None


async def _fetch_real_benchmarks() -> Optional[dict]:
    try:
        import yfinance as yf
        import asyncio
        t = await asyncio.to_thread(yf.Ticker, "ID10Y=RR")
        info = await asyncio.to_thread(lambda: t.info)
        if info and info.get("regularMarketPrice"):
            ytm = float(info["regularMarketPrice"])
            prev = float(info.get("regularMarketPreviousClose", ytm))
            change = round(ytm - prev, 2)
            return {
                "bonds": [
                    {"isin": "IDG000010101", "name": "FR0100", "tenor": "10Y", "coupon": 6.50, "ytm": ytm, "price": round(100 - (ytm - 6.5) * 2, 2), "change": change, "volume": 4500},
                ],
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "live",
            }
    except Exception as e:
        logger.warning(f"Failed to fetch real benchmarks: {e}")
    return None


@router.get("/yield-curve")
async def get_yield_curve():
    real = await _fetch_real_yield_curve()
    if real:
        return real
    return _SIMULATED_YIELD_CURVE


@router.get("/benchmarks")
async def get_benchmark_bonds():
    real = await _fetch_real_benchmarks()
    if real:
        return real
    return _SIMULATED_BENCHMARKS


@router.get("/cds")
async def get_cds():
    return _SIMULATED_CDS


@router.get("/auctions")
async def get_auctions():
    return _SIMULATED_AUCTIONS
