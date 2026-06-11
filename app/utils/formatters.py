from datetime import datetime, timezone
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")


def format_rupiah(value: float) -> str:
    return f"Rp{value:,.0f}"


def format_usd(value: float) -> str:
    return f"${value:,.2f}"


def format_pct(value: float) -> str:
    return f"{value:+.2f}%"


def format_change(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:,.2f}"


def now_wib() -> datetime:
    return datetime.now(WIB)


def parse_iso_wib(iso_str: str) -> datetime:
    dt = datetime.fromisoformat(iso_str)
    return dt.astimezone(WIB)
