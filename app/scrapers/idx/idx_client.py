import asyncio
import httpx
from app.utils.logger import logger

BROWSER_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Referer": "https://www.idx.co.id/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


class IDXClient:
    def __init__(self):
        self._cookies = {}
        self._session_ready = False

    async def _ensure_session(self):
        if self._session_ready:
            return
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get("https://www.idx.co.id/id", headers={
                "User-Agent": BROWSER_HEADERS["User-Agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            })
            for cookie in resp.cookies.jar:
                self._cookies[cookie.name] = cookie.value
            await asyncio.sleep(1)
            val = await client.get(
                "https://www.idx.co.id/primary/home/GetIndexList",
                headers={**BROWSER_HEADERS, "Cookie": "; ".join(f"{k}={v}" for k, v in self._cookies.items())},
            )
            for cookie in val.cookies.jar:
                self._cookies[cookie.name] = cookie.value
        self._session_ready = True

    def _cookie_header(self):
        return "; ".join(f"{k}={v}" for k, v in self._cookies.items())

    def _headers(self):
        return {**BROWSER_HEADERS, "Cookie": self._cookie_header()}

    async def _get(self, url: str, retries: int = 3) -> dict | list | None:
        await self._ensure_session()
        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                    resp = await client.get(url, headers=self._headers())
                    if resp.status_code >= 500:
                        raise IOError(f"HTTP {resp.status_code}")
                    return resp.json()
            except Exception as e:
                logger.warning(f"IDX GET {url} failed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    await asyncio.sleep(1.5 * attempt)
        return None


_idx_client = IDXClient()


async def idx_get(url: str) -> dict | list | None:
    return await _idx_client._get(url)
