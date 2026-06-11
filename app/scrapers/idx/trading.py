from datetime import datetime
from app.scrapers.idx.idx_client import idx_get


async def get_stock_summary(date: str | None = None):
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    data = await idx_get(
        f"https://www.idx.co.id/primary/TradingSummary/GetStockSummary?date={date}"
    )
    if not data or not isinstance(data.get("data"), list):
        return None
    return [
        {
            "code": i.get("StockCode", ""),
            "name": i.get("StockName", ""),
            "date": i.get("Date", ""),
            "open": i.get("OpenPrice", 0),
            "high": i.get("High", 0),
            "low": i.get("Low", 0),
            "close": i.get("Close", 0),
            "previous": i.get("Previous", 0),
            "change": i.get("Change", 0),
            "volume": i.get("Volume", 0),
            "value": i.get("Value", 0),
            "frequency": i.get("Frequency", 0),
            "bid": i.get("Bid", 0),
            "bid_volume": i.get("BidVolume", 0),
            "offer": i.get("Offer", 0),
            "offer_volume": i.get("OfferVolume", 0),
            "foreign_buy": i.get("ForeignBuy", 0),
            "foreign_sell": i.get("ForeignSell", 0),
            "foreign_net": i.get("ForeignBuy", 0) - i.get("ForeignSell", 0),
            "listed_shares": i.get("ListedShares", 0),
        }
        for i in data["data"]
    ]


async def get_top_gainers(year: int | None = None, month: int | None = None):
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    import json, base64
    query = base64.b64encode(json.dumps({"year": str(y), "month": str(m), "quarter": 0, "type": "monthly"}).encode()).decode()
    data = await idx_get(
        f"https://www.idx.co.id/primary/DigitalStatistic/GetApiData?urlName=LINK_TOP_GAINER&query={query}&isPrint=False&cumulative=false"
    )
    if not data or not isinstance(data.get("data"), list):
        return None
    return [
        {
            "code": i.get("Code", ""),
            "name": i.get("StockName", ""),
            "close": i.get("closeValue", 0),
            "previous": i.get("prevValue", 0),
            "change": i.get("changePrice", 0),
            "percent": i.get("changePercentage", 0),
            "dilution": i.get("dilution", 0),
        }
        for i in data["data"]
    ]


async def get_top_losers(year: int | None = None, month: int | None = None):
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    import json, base64
    query = base64.b64encode(json.dumps({"year": str(y), "month": str(m), "quarter": 0, "type": "monthly"}).encode()).decode()
    data = await idx_get(
        f"https://www.idx.co.id/primary/DigitalStatistic/GetApiData?urlName=LINK_TOP_LOSER&query={query}&isPrint=False&cumulative=false"
    )
    if not data or not isinstance(data.get("data"), list):
        return None
    return [
        {
            "code": i.get("Code", ""),
            "name": i.get("StockName", ""),
            "close": i.get("closeValue", 0),
            "previous": i.get("prevValue", 0),
            "change": i.get("changePrice", 0),
            "percent": i.get("changePercentage", 0),
            "dilution": i.get("dilution", 0),
        }
        for i in data["data"]
    ]


async def get_trading_info_daily(code: str):
    data = await idx_get(
        f"https://www.idx.co.id/primary/ListedCompany/GetTradingInfoDaily?code={code}"
    )
    if not data or not data.get("SecurityCode"):
        return None
    return {
        "code": data.get("SecurityCode", ""),
        "board": data.get("BoardCode", ""),
        "previous": data.get("PreviousPrice", 0),
        "open": data.get("OpeningPrice", 0),
        "high": data.get("HighestPrice", 0),
        "low": data.get("LowestPrice", 0),
        "close": data.get("ClosingPrice", 0),
        "change": data.get("Change", 0),
        "volume": data.get("TradedVolume", 0),
        "value": data.get("TradedValue", 0),
        "frequency": data.get("TradedFrequency", 0),
        "bid": data.get("BestBidPrice", 0),
        "bid_volume": data.get("BestBidVolume", 0),
        "offer": data.get("BestOfferPrice", 0),
        "offer_volume": data.get("BestOfferVolume", 0),
    }
