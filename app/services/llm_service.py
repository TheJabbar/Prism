from typing import Optional, AsyncIterator
from openai import AsyncOpenAI
from app.config import settings
from app.utils.logger import logger


class LLMService:
    def __init__(self):
        self._provider = settings.llm_provider
        self._openrouter_client: Optional[AsyncOpenAI] = None
        self._groq_client: Optional[AsyncOpenAI] = None

    def _get_openrouter(self) -> AsyncOpenAI:
        if self._openrouter_client is None:
            self._openrouter_client = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
            )
        return self._openrouter_client

    def _get_groq(self) -> AsyncOpenAI:
        if self._groq_client is None:
            self._groq_client = AsyncOpenAI(
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url,
            )
        return self._groq_client

    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> str:
        if self._provider == "openrouter":
            try:
                client = self._get_openrouter()
                model = settings.llm_model.replace("openrouter:", "")
                resp = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                )
                if stream:
                    return resp
                return resp.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"OpenRouter failed, falling back to Groq: {e}")
                return await self._groq_fallback(messages, temperature, max_tokens, stream)
        else:
            return await self._groq_fallback(messages, temperature, max_tokens, stream)

    async def _groq_fallback(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> str:
        client = self._get_groq()
        model = settings.groq_model.replace("groq:", "")
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        if stream:
            return resp
        return resp.choices[0].message.content or ""

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        if self._provider == "openrouter":
            try:
                client = self._get_openrouter()
                model = settings.llm_model.replace("openrouter:", "")
                stream = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield delta
                return
            except Exception as e:
                logger.warning(f"OpenRouter stream failed, falling back to Groq: {e}")

        client = self._get_groq()
        model = settings.groq_model.replace("groq:", "")
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

    async def generate_daily_insight(self, market_data: dict) -> str:
        prompt = f"""You are PRISM AI, a confident data-driven Indonesian financial market analyst.

=== TODAY'S MARKET DATA ===
- IHSG: {market_data.get('ihsg', 'N/A')} ({market_data.get('ihsg_change', 'N/A')})
- USD/IDR: {market_data.get('usdidr', 'N/A')}
- BI Rate: {market_data.get('bi_rate', 'N/A')}
- 10Y SBN Yield: {market_data.get('sbn_10y', 'N/A')}
- CPI YoY: {market_data.get('cpi_yoy', 'N/A')}
- Core Inflation: {market_data.get('core_inflation', 'N/A')}
- GDP Growth: {market_data.get('gdp_growth', 'N/A')}
- Brent: {market_data.get('brent', 'N/A')}
- DXY: {market_data.get('dxy', 'N/A')}

Recent news headlines: {market_data.get('headlines', 'N/A')}

Generate a bilingual (Indonesian + English) daily market briefing.
Be direct and analytical — this is for professional traders/investors.
Sections:
- Market Summary / Ringkasan Pasar
- Key Drivers / Faktor Penggerak
- Sector Calls / Rekomendasi Sektor (give clear overweight/neutral/underweight views)
- Risk Watch / Pantauan Risiko
- Today's Calendar / Kalender Hari Ini

Base all views on the data provided. You are an analyst — give clear, reasoned opinions."""
        messages = [
            {"role": "system", "content": "You are PRISM AI, a confident data-driven Indonesian financial market analyst."},
            {"role": "user", "content": prompt},
        ]
        return await self.chat_completion(messages, temperature=0.7, max_tokens=4096)


llm_service = LLMService()
