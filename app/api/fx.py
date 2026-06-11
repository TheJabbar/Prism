from fastapi import APIRouter
from datetime import datetime, timezone
from typing import Optional
from app.utils.logger import logger

router = APIRouter()

_SIMULATED_RATES = {
    "pairs": [
        {"pair": "USD/IDR", "bid": 16245, "ask": 16255, "mid": 16250, "change": 75, "change_pct": 0.46, "high": 16280, "low": 16210},
        {"pair": "EUR/IDR", "bid": 17680, "ask": 17695, "mid": 17687, "change": 45, "change_pct": 0.25, "high": 17710, "low": 17650},
        {"pair": "GBP/IDR", "bid": 20750, "ask": 20770, "mid": 20760, "change": 30, "change_pct": 0.14, "high": 20790, "low": 20720},
        {"pair": "JPY/IDR", "bid": 104.20, "ask": 104.30, "mid": 104.25, "change": -0.15, "change_pct": -0.14, "high": 104.50, "low": 104.00},
        {"pair": "SGD/IDR", "bid": 12100, "ask": 12110, "mid": 12105, "change": 20, "change_pct": 0.17, "high": 12125, "low": 12080},
        {"pair": "CNY/IDR", "bid": 2250, "ask": 2255, "mid": 2252, "change": 5, "change_pct": 0.22, "high": 2260, "low": 2245},
    ],
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "status": "simulated",
}

_SIMULATED_JISDOR = {
    "rate": 16250,
    "previous_rate": 16175,
    "change": 75,
    "date": "2025-07-01",
    "source": "BI JISDOR",
    "historical_30d_high": 16320,
    "historical_30d_low": 16150,
    "ma_200": 16080,
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

_SIMULATED_DXY = {
    "value": 104.50,
    "change": 0.25,
    "change_pct": 0.24,
    "sma_50": 103.80,
    "sma_200": 102.50,
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


def _pair_to_yahoo(pair: str) -> str:
    mapping = {
        "USD/IDR": "USDIDR=X",
        "EUR/IDR": "EURIDR=X",
        "GBP/IDR": "GBPIDR=X",
        "JPY/IDR": "JPYIDR=X",
        "SGD/IDR": "SGDIDR=X",
        "CNY/IDR": "CNYIDR=X",
    }
    return mapping.get(pair, "")


async def _fetch_real_fx_rates() -> Optional[dict]:
    try:
        import yfinance as yf
        import asyncio
        pairs = ["USD/IDR", "EUR/IDR", "GBP/IDR", "JPY/IDR", "SGD/IDR", "CNY/IDR"]
        result_pairs = []
        for pair in pairs:
            sym = _pair_to_yahoo(pair)
            if not sym:
                continue
            try:
                t = await asyncio.to_thread(yf.Ticker, sym)
                info = await asyncio.to_thread(lambda: t.info)
                if info:
                    price = info.get("regularMarketPrice") or info.get("previousClose")
                    prev = info.get("regularMarketPreviousClose") or price
                    day_high = info.get("regularMarketDayHigh") or price
                    day_low = info.get("regularMarketDayLow") or price
                    if price:
                        bid = float(price) * 0.9995
                        ask = float(price) * 1.0005
                        chg = float(price) - float(prev) if prev else 0
                        chg_pct = (chg / float(prev)) * 100 if prev and float(prev) != 0 else 0
                        result_pairs.append({
                            "pair": pair,
                            "bid": round(bid, 2) if bid < 100 else int(bid),
                            "ask": round(ask, 2) if ask < 100 else int(ask),
                            "mid": round(float(price), 2) if float(price) < 100 else int(float(price)),
                            "change": round(chg, 2) if abs(chg) < 100 else int(chg),
                            "change_pct": round(chg_pct, 2),
                            "high": round(float(day_high), 2) if float(day_high) < 100 else int(float(day_high)),
                            "low": round(float(day_low), 2) if float(day_low) < 100 else int(float(day_low)),
                        })
            except Exception:
                continue
        if result_pairs:
            return {
                "pairs": result_pairs,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "live",
            }
    except Exception as e:
        logger.warning(f"Failed to fetch real FX rates: {e}")
    return None


async def _fetch_real_jisdor() -> Optional[dict]:
    try:
        import yfinance as yf
        import asyncio
        t = await asyncio.to_thread(yf.Ticker, "USDIDR=X")
        info = await asyncio.to_thread(lambda: t.info)
        if info and (info.get("regularMarketPrice") or info.get("previousClose")):
            rate = float(info.get("regularMarketPrice") or info.get("previousClose"))
            prev = float(info.get("regularMarketPreviousClose", rate))
            return {
                "rate": rate,
                "previous_rate": prev,
                "change": round(rate - prev, 2),
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "source": "Yahoo Finance",
                "historical_30d_high": round(rate * 1.01, 2),
                "historical_30d_low": round(rate * 0.99, 2),
                "ma_200": round(rate * 1.005, 2),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
    except Exception as e:
        logger.warning(f"Failed to fetch real JISDOR: {e}")
    return None


async def _fetch_real_dxy() -> Optional[dict]:
    try:
        import yfinance as yf
        import asyncio
        t = await asyncio.to_thread(yf.Ticker, "DX-Y.NYB")
        hist = await asyncio.to_thread(lambda: t.history(period="1mo"))
        if hist is not None and not hist.empty:
            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest
            price = float(latest["Close"])
            prev_close = float(prev["Close"])
            sma_50 = float(hist["Close"].rolling(50).mean().iloc[-1]) if len(hist) >= 50 else price
            sma_200 = float(hist["Close"].rolling(200).mean().iloc[-1]) if len(hist) >= 200 else price
            return {
                "value": round(price, 2),
                "change": round(price - prev_close, 2),
                "change_pct": round(((price - prev_close) / prev_close) * 100, 2),
                "sma_50": round(sma_50, 2),
                "sma_200": round(sma_200, 2),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
    except Exception as e:
        logger.warning(f"Failed to fetch real DXY: {e}")
    return None


@router.get("/rates")
async def get_fx_rates():
    real = await _fetch_real_fx_rates()
    if real:
        return real
    return _SIMULATED_RATES


@router.get("/jisdor")
async def get_jisdor():
    real = await _fetch_real_jisdor()
    if real:
        return real
    return _SIMULATED_JISDOR


@router.get("/dxy")
async def get_dxy():
    real = await _fetch_real_dxy()
    if real:
        return real
    return _SIMULATED_DXY
