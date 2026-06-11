from datetime import datetime, timezone
from app.utils.logger import logger
from app.scrapers.market.bi_scraper import get_latest_bi_rate, get_bi_rate_history


class IndicatorService:
    async def get_all_indicators(self) -> dict:
        bi = get_latest_bi_rate()
        history = get_bi_rate_history()
        prev_rate = history[1]["bi_7drr"] if len(history) > 1 else bi["rate"]

        bi_history_monthly = [
            {"date": r["date"][:7], "value": r["bi_7drr"]}
            for r in history if len(r["date"]) >= 7
        ]
        deposit_history = [
            {"date": h["date"][:7], "value": h["deposit_facility"]}
            for h in history if len(h["date"]) >= 7
        ]
        lending_history = [
            {"date": h["date"][:7], "value": h["lending_facility"]}
            for h in history if len(h["date"]) >= 7
        ]

        return {
            "monetary_policy": [
                {
                    "name": "BI-7DRR", "value": bi["rate"],
                    "previous": prev_rate, "unit": "%",
                    "change": round(bi["rate"] - prev_rate, 2),
                    "history": bi_history_monthly,
                },
                {
                    "name": "Deposit Facility Rate", "value": bi["deposit_facility"],
                    "previous": bi["deposit_facility"], "unit": "%", "change": 0.0,
                    "history": deposit_history,
                },
                {
                    "name": "Lending Facility Rate", "value": bi["lending_facility"],
                    "previous": bi["lending_facility"], "unit": "%", "change": 0.0,
                    "history": lending_history,
                },
                {
                    "name": "Reserve Requirement (GWM)", "value": 9.0,
                    "previous": 9.0, "unit": "%", "change": 0.0,
                },
            ],
            "inflation": [
                {"name": "CPI YoY", "value": 2.84, "previous": 2.91, "unit": "%", "change": -0.07},
                {"name": "CPI MoM", "value": 0.12, "previous": 0.18, "unit": "%", "change": -0.06},
                {"name": "Core Inflation YoY", "value": 1.90, "previous": 1.93, "unit": "%", "change": -0.03},
            ],
            "growth": [
                {"name": "GDP Growth YoY", "value": 5.11, "previous": 5.05, "unit": "%", "change": 0.06},
                {"name": "GDP Growth QoQ", "value": 1.34, "previous": 1.62, "unit": "%", "change": -0.28},
            ],
            "external_sector": [
                {"name": "Trade Balance", "value": 2.15, "previous": 1.85, "unit": "USD bn", "change": 0.30},
                {"name": "Foreign Exchange Reserves", "value": 145.2, "previous": 143.8, "unit": "USD bn", "change": 1.4},
                {"name": "Debt-to-GDP Ratio", "value": 39.0, "previous": 38.7, "unit": "%", "change": 0.3},
            ],
            "banking": [
                {"name": "CAR", "value": 26.5, "previous": 26.2, "unit": "%", "change": 0.3},
                {"name": "NPL", "value": 2.15, "previous": 2.20, "unit": "%", "change": -0.05},
                {"name": "LDR", "value": 82.5, "previous": 82.1, "unit": "%", "change": 0.4},
                {"name": "NIM", "value": 4.65, "previous": 4.70, "unit": "%", "change": -0.05},
            ],
            "fiscal": [
                {"name": "Budget Deficit (% GDP)", "value": 2.8, "previous": 2.5, "unit": "%", "change": 0.3},
                {"name": "Tax Revenue YTD", "value": 1850.5, "previous": 1720.3, "unit": "IDR tn", "change": 130.2},
                {"name": "Government Bond Outstanding", "value": 5400.0, "previous": 5300.0, "unit": "IDR tn", "change": 100.0},
            ],
            "bi_rate_history": get_bi_rate_history(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": bi["status"],
            "source": bi["source"],
        }

    async def get_global_indicators(self) -> list[dict]:
        return [
            {"name": "DXY", "value": 104.50, "change": 0.25, "unit": "index"},
            {"name": "US Fed Funds Rate", "value": 5.50, "change": 0.0, "unit": "%"},
            {"name": "US CPI YoY", "value": 3.4, "change": -0.1, "unit": "%"},
            {"name": "US 10Y Yield", "value": 4.28, "change": 0.02, "unit": "%"},
            {"name": "Brent Crude", "value": 82.30, "change": 0.85, "unit": "USD/bbl"},
            {"name": "CPO", "value": 3890, "change": -25, "unit": "MYR/MT"},
            {"name": "Nickel", "value": 17200, "change": 200, "unit": "USD/MT"},
            {"name": "Coal", "value": 125.50, "change": -2.30, "unit": "USD/MT"},
            {"name": "Gold", "value": 2330.0, "change": 12.5, "unit": "USD/oz"},
            {"name": "VIX", "value": 14.2, "change": -0.8, "unit": "index"},
        ]


indicator_service = IndicatorService()
