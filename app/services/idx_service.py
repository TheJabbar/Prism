from app.scrapers.idx import market, trading, company
from app.utils.logger import logger


class IDXService:
    async def get_overview(self) -> dict:
        results = await self._gather(
            market.get_index_list(),
            market.get_trade_summary(),
            trading.get_top_gainers(),
            trading.get_top_losers(),
        )
        return {
            "indices": results[0] if isinstance(results[0], list) else [],
            "trade_summary": results[1] if isinstance(results[1], list) else [],
            "top_gainers": (results[2] if isinstance(results[2], list) else [])[:10],
            "top_losers": (results[3] if isinstance(results[3], list) else [])[:10],
        }

    async def get_indices(self):
        return await market.get_index_list()

    async def get_trade_summary(self):
        return await market.get_trade_summary()

    async def get_index_chart(self, code: str, period: str = "1M"):
        return await market.get_index_chart(code, period)

    async def get_top_gainers(self):
        return await trading.get_top_gainers()

    async def get_top_losers(self):
        return await trading.get_top_losers()

    async def get_stock_summary(self, date: str | None = None):
        return await trading.get_stock_summary(date)

    async def get_trading_info(self, code: str):
        return await trading.get_trading_info_daily(code)

    async def get_stock_screener(self, sector: str = "", sub_sector: str = ""):
        return await company.get_stock_screener(sector, sub_sector)

    async def get_financial_ratios(self, year: int | None = None, month: int | None = None):
        return await company.get_financial_ratios(year, month)

    async def get_company_profiles(self, start: int = 0, length: int = 100):
        return await company.get_company_profiles(start, length)

    async def get_company_detail(self, code: str):
        return await company.get_company_detail(code)

    async def _gather(self, *coros):
        import asyncio
        return await asyncio.gather(*coros, return_exceptions=True)


idx_service = IDXService()
