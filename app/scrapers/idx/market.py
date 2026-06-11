from app.scrapers.idx.idx_client import idx_get

async def get_index_list():
    data = await idx_get("https://www.idx.co.id/primary/home/GetIndexList")
    if not isinstance(data, list):
        return None
    return [
        {
            "code": i.get("IndexCode", ""),
            "name": i.get("IndexCode", ""),
            "close": i.get("Closing", ""),
            "change": i.get("Change", ""),
            "percent": i.get("Percent", ""),
            "current": i.get("Current", ""),
        }
        for i in data
    ]


async def get_trade_summary():
    data = await idx_get("https://www.idx.co.id/primary/Home/GetTradeSummary?lang=id")
    if not isinstance(data, list):
        return None
    return [
        {
            "segment": i.get("DESCRIPTION", ""),
            "volume": i.get("Volume", 0),
            "value": i.get("Value", 0),
            "frequency": i.get("Frequency", 0),
            "date": i.get("Dates", ""),
        }
        for i in data
    ]


async def get_index_chart(index_code: str, period: str = "1M"):
    data = await idx_get(
        f"https://www.idx.co.id/primary/helper/GetIndexChart?indexCode={index_code}&period={period}"
    )
    if not data or not data.get("ChartData"):
        return None
    return {
        "code": data.get("IndexCode", index_code),
        "open": data.get("OpenPrice"),
        "high": data.get("MaxPrice"),
        "low": data.get("MinPrice"),
        "chart": [
            {"date": p.get("Date", ""), "value": p.get("Close", 0)}
            for p in data["ChartData"]
        ],
    }
