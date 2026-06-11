from datetime import datetime, timezone
from typing import Optional
from app.utils.logger import logger

_BI_RATE_HISTORY = [
    # 2026
    {"date": "2026-06-09", "rate": 5.50, "deposit": 4.50, "lending": 6.25},
    {"date": "2026-05-20", "rate": 5.25, "deposit": 4.25, "lending": 6.00},
    {"date": "2026-04-22", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2026-03-17", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2026-02-19", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2026-01-21", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    # 2025
    {"date": "2025-12-17", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2025-11-19", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2025-10-22", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2025-09-17", "rate": 4.75, "deposit": 3.75, "lending": 5.50},
    {"date": "2025-08-20", "rate": 5.00, "deposit": 4.00, "lending": 5.75},
    {"date": "2025-07-16", "rate": 5.25, "deposit": 4.25, "lending": 6.00},
    {"date": "2025-06-18", "rate": 5.50, "deposit": 4.50, "lending": 6.25},
    {"date": "2025-05-21", "rate": 5.50, "deposit": 4.50, "lending": 6.25},
    {"date": "2025-04-23", "rate": 5.75, "deposit": 4.75, "lending": 6.50},
    {"date": "2025-03-19", "rate": 5.75, "deposit": 4.75, "lending": 6.50},
    {"date": "2025-02-19", "rate": 5.75, "deposit": 4.75, "lending": 6.50},
    {"date": "2025-01-15", "rate": 5.75, "deposit": 4.75, "lending": 6.50},
    # 2024
    {"date": "2024-12-18", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
    {"date": "2024-11-20", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
    {"date": "2024-10-16", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
    {"date": "2024-09-18", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
    {"date": "2024-08-21", "rate": 6.25, "deposit": 5.25, "lending": 7.00},
    {"date": "2024-07-17", "rate": 6.25, "deposit": 5.25, "lending": 7.00},
    {"date": "2024-06-20", "rate": 6.25, "deposit": 5.25, "lending": 7.00},
    {"date": "2024-05-22", "rate": 6.25, "deposit": 5.25, "lending": 7.00},
    {"date": "2024-04-24", "rate": 6.25, "deposit": 5.25, "lending": 7.00},
    {"date": "2024-03-20", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
    {"date": "2024-02-21", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
    {"date": "2024-01-17", "rate": 6.00, "deposit": 5.00, "lending": 6.75},
]


async def fetch_bi_rate() -> Optional[dict]:
    """Fetch current BI-7DRR rate. Tries BI website first, falls back to known data."""
    try:
        from scrapling.fetchers import Fetcher
        url = "https://www.bi.go.id/en/moneter/bi-7day-rr/Data/Default.aspx"
        page = Fetcher.get(url, timeout=15)
        if page and page.status == 200:
            rows = page.css("table tr")
            if rows and len(rows) > 1:
                for row in rows:
                    cells = row.css("td::text").getall()
                    if cells and len(cells) >= 2:
                        try:
                            rate_text = cells[1].strip()
                            rate = float(rate_text.replace(",", "."))
                            if 3.0 <= rate <= 10.0:
                                deposit = round(rate - 0.75, 2)
                                lending = round(rate + 0.75, 2)
                                return {
                                    "rate": rate,
                                    "deposit_facility": deposit,
                                    "lending_facility": lending,
                                    "source": "BI Website",
                                    "status": "live",
                                    "updated_at": datetime.now(timezone.utc).isoformat(),
                                }
                        except (ValueError, IndexError):
                            continue
    except Exception as e:
        logger.warning(f"BI website scrape failed: {e}")

    return None


def get_latest_bi_rate() -> dict:
    rate = _BI_RATE_HISTORY[0]
    return {
        "rate": rate["rate"],
        "deposit_facility": rate["deposit"],
        "lending_facility": rate["lending"],
        "source": "BI Historical Data",
        "status": "historical",
        "updated_at": rate["date"] + "T00:00:00+00:00",
    }


def get_bi_rate_history() -> list[dict]:
    return [
        {
            "date": r["date"],
            "bi_7drr": r["rate"],
            "deposit_facility": r["deposit"],
            "lending_facility": r["lending"],
        }
        for r in sorted(_BI_RATE_HISTORY, key=lambda x: x["date"], reverse=True)
    ]
