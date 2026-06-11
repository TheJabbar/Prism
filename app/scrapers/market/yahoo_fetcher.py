import asyncio
from datetime import datetime, timezone
from typing import Optional
from app.utils.logger import logger

_SYMBOL_MAP = {
    "IHSG": "^JKSE",
    "LQ45": "^JKLQ45",
    "BBCA": "BBCA.JK",
    "BBRI": "BBRI.JK",
    "TLKM": "TLKM.JK",
    "ASII": "ASII.JK",
    "BMRI": "BMRI.JK",
    "UNVR": "UNVR.JK",
    "ADRO": "ADRO.JK",
    "BYAN": "BYAN.JK",
    "GOTO": "GOTO.JK",
    "CPIN": "CPIN.JK",
    "ICBP": "ICBP.JK",
    "INDF": "INDF.JK",
    "ANTM": "ANTM.JK",
    "ITMG": "ITMG.JK",
    "PTBA": "PTBA.JK",
    "PGAS": "PGAS.JK",
    "SMGR": "SMGR.JK",
    "BBNI": "BBNI.JK",
    "ARTO": "ARTO.JK",
    "BRIS": "BRIS.JK",
    "MDKA": "MDKA.JK",
    "DXY": "DX-Y.NYB",
    "Brent": "BZ=F",
    "Gold": "GC=F",
    "CPO": "GC=F",
    "USD/IDR": "USDIDR=X",
    "EUR/IDR": "EURIDR=X",
}


async def fetch_ticker_data(symbol: str) -> Optional[dict]:
    yahoo_symbol = _SYMBOL_MAP.get(symbol)
    if not yahoo_symbol:
        logger.warning(f"No Yahoo Finance mapping for {symbol}")
        return None
    try:
        import yfinance as yf
        ticker = await asyncio.to_thread(yf.Ticker, yahoo_symbol)
        info = await asyncio.to_thread(lambda: ticker.info)
        if not info or info.get("regularMarketPrice") is None:
            hist = await asyncio.to_thread(
                lambda: ticker.history(period="2d")
            )
            if hist is not None and not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                price = float(latest["Close"])
                prev_close = float(prev["Close"])
                change = price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
                volume = float(latest["Volume"]) if "Volume" in latest else 0
                return {
                    "symbol": symbol,
                    "last_price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "volume": volume,
                    "timestamp": datetime.now(timezone.utc),
                }
            return None
        price = info.get("regularMarketPrice") or info.get("previousClose") or 0
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose") or price
        change = price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0
        volume = info.get("regularMarketVolume") or 0
        return {
            "symbol": symbol,
            "last_price": round(float(price), 2),
            "change": round(float(change), 2),
            "change_pct": round(float(change_pct), 2),
            "volume": float(volume) if volume else 0,
            "timestamp": datetime.now(timezone.utc),
        }
    except Exception as e:
        logger.warning(f"Yahoo Finance fetch failed for {symbol}: {e}")
        return None


async def fetch_ticker_history(symbol: str) -> list:
    yahoo_symbol = _SYMBOL_MAP.get(symbol)
    if not yahoo_symbol:
        return []
    try:
        import yfinance as yf
        ticker = await asyncio.to_thread(yf.Ticker, yahoo_symbol)
        hist = await asyncio.to_thread(lambda: ticker.history(period="1mo"))
        if hist is None or hist.empty:
            return []
        return [
            {"date": str(idx.date()), "value": round(float(row["Close"]), 2)}
            for idx, row in hist.iterrows()
        ]
    except Exception as e:
        logger.warning(f"History fetch failed for {symbol}: {e}")
        return []


async def fetch_market_summary() -> dict:
    symbols = ["IHSG", "LQ45", "USD/IDR", "DXY", "Brent", "Gold"]
    tasks = [fetch_ticker_data(s) for s in symbols]
    hist_tasks = [fetch_ticker_history(s) for s in symbols]
    results, hist_results = await asyncio.gather(
        asyncio.gather(*tasks, return_exceptions=True),
        asyncio.gather(*hist_tasks, return_exceptions=True),
    )
    data = {}
    for sym, res, hist in zip(symbols, results, hist_results):
        if isinstance(res, dict) and res.get("last_price"):
            is_up = res["change"] >= 0
            h = hist if isinstance(hist, list) and len(hist) > 1 else []
            data[sym.lower().replace("/", "")] = {
                "last": res["last_price"],
                "change": res["change"],
                "change_pct": res["change_pct"],
                "status": "up" if is_up else "down",
                "history": h,
            }
    return data


async def fetch_all_tickers() -> list[dict]:
    symbols = list(_SYMBOL_MAP.keys())
    tasks = [fetch_ticker_data(s) for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    tickers = []
    for sym, res in zip(symbols, results):
        if isinstance(res, dict) and res.get("last_price"):
            snap_type = "index"
            if sym in ("DXY",):
                snap_type = "index"
            elif sym in ("USD/IDR", "EUR/IDR"):
                snap_type = "fx"
            elif sym in ("Brent", "Gold", "CPO"):
                snap_type = "commodity"
            elif sym in ("IHSG", "LQ45"):
                snap_type = "index"
            else:
                snap_type = "equity"
            tickers.append({
                "symbol": sym,
                "type": snap_type,
                "last_price": res["last_price"],
                "change": res["change"],
                "change_pct": res["change_pct"],
                "volume": res["volume"],
                "timestamp": res["timestamp"],
            })
    return tickers
