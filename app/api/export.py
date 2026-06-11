from fastapi import APIRouter, Response
from datetime import datetime, timezone
from app.scrapers.market.bi_scraper import get_latest_bi_rate
from app.scrapers.market.yahoo_fetcher import fetch_all_tickers, fetch_market_summary
import csv
import io
import json

router = APIRouter()


@router.get("/csv", summary="Export data as CSV")
async def export_csv(module: str = "market"):
    data = await _get_export_data(module)
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=prism_{module}_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.get("/json", summary="Export data as JSON")
async def export_json(module: str = "market"):
    data = await _get_export_data(module)
    return Response(
        content=json.dumps(data, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=prism_{module}_{datetime.now().strftime('%Y%m%d')}.json"},
    )


async def _get_export_data(module: str) -> list[dict]:
    if module == "market":
        tickers = await fetch_all_tickers()
        if tickers:
            return [
                {"Symbol": t["symbol"], "Price": t["last_price"], "Change": t["change"], "Change%": t["change_pct"]}
                for t in tickers[:10]
            ]
        return [
            {"Symbol": "IHSG", "Price": 6845.32, "Change": -23.45, "Change%": -0.34},
            {"Symbol": "LQ45", "Price": 912.45, "Change": -5.67, "Change%": -0.62},
            {"Symbol": "USD/IDR", "Price": 16250, "Change": 75, "Change%": 0.46},
        ]
    elif module == "indicators":
        bi = get_latest_bi_rate()
        return [
            {"Indicator": "BI-7DRR", "Value": bi["rate"], "Unit": "%"},
            {"Indicator": "Deposit Facility Rate", "Value": bi["deposit_facility"], "Unit": "%"},
            {"Indicator": "Lending Facility Rate", "Value": bi["lending_facility"], "Unit": "%"},
            {"Indicator": "CPI YoY", "Value": 2.84, "Unit": "%"},
            {"Indicator": "GDP Growth", "Value": 5.11, "Unit": "%"},
        ]
    elif module == "portfolio":
        return [
            {"Ticker": "BBCA", "Quantity": 1000, "Avg Price": 9500, "Last Price": 10250, "P&L%": 7.89},
            {"Ticker": "BBRI", "Quantity": 2000, "Avg Price": 5400, "Last Price": 5850, "P&L%": 8.33},
        ]
    return []
