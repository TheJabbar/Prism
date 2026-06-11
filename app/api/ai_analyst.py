import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import llm_service
from app.services.market_service import market_service
from app.services.news_service import news_service
from app.services.indicator_service import indicator_service
from app.utils.logger import logger

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: Optional[list[dict]] = None


class InsightRequest(BaseModel):
    include_headlines: bool = True


async def _build_context(req: ChatRequest) -> tuple[list[dict], str]:
    summary = await market_service.get_market_summary()
    indicators = await indicator_service.get_all_indicators()
    headlines = await news_service.get_news(limit=10)

    news_text = ""
    for h in headlines:
        news_text += f"- [{h['source']}] {h['title']}\n"

    mp = indicators.get("monetary_policy", [])
    inf = indicators.get("inflation", [])
    growth = indicators.get("growth", [])
    ext = indicators.get("external_sector", [])
    bank = indicators.get("banking", [])

    system_prompt = (
        "You are PRISM AI, a confident and data-driven Indonesian financial market analyst.\n"
        "You have access to live market data and macroeconomic indicators. "
        "Your job is to analyze the data and provide reasoned, actionable insights.\n"
        "\n=== LIVE MARKET DATA ===\n"
        f"IHSG: {summary['ihsg']['last']} ({summary['ihsg']['change_pct']:+.2f}%)\n"
        f"USD/IDR: {summary['usdidr']['last']}\n"
        f"BI-7DRR: {summary['bi_rate']}%\n"
        f"10Y SBN Yield: {summary['sbn_10y']}%\n"
        f"Brent Crude: ${summary['brent']}\n"
        f"DXY: {summary['dxy']}\n"
        f"\n=== MACRO INDICATORS ===\n"
        f"Inflation: CPI YoY {inf[0]['value']}% (prev {inf[0]['previous']}%), Core {inf[1]['value']}%\n"
        f"GDP Growth: {growth[0]['value']}% YoY\n"
        f"Trade Balance: ${ext[0]['value']}B, FX Reserves: ${ext[1]['value']}B\n"
        f"Banking: NPL {bank[1]['value']}%, CAR {bank[0]['value']}%, LDR {bank[2]['value']}%\n"
        f"\n=== RECENT NEWS HEADLINES ===\n{news_text}\n"
        "\n=== BEHAVIOR ===\n"
        "1. Be direct, confident, and data-driven. You are an analyst, not a disclaimer machine.\n"
        "2. When asked about specific stocks, sectors, or strategies, reference the data above and provide your best analysis.\n"
        "3. You CAN discuss specific stocks, price levels, and trading ideas based on the data. "
        "Frame recommendations with risk context, but don't be afraid to give a clear opinion.\n"
        "4. Use exact numbers from the data. Don't make up figures.\n"
        "5. Respond in the same language the user writes in (Indonesian or English).\n"
        "6. When suggesting entry/exit levels, always note key support/resistance and risk factors.\n"
        "7. You are not a regulated advisor — you are an AI analyst providing data-backed research. Be useful."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if req.history:
        messages.extend(req.history)
    messages.append({"role": "user", "content": req.message})
    return messages, llm_service._provider


@router.post("/chat")
async def ai_chat(req: ChatRequest):
    try:
        messages, provider = await _build_context(req)
        content = await llm_service.chat_completion(messages, temperature=0.7, max_tokens=4096)
        return {"response": content, "model_provider": provider}
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
        return {
            "response": "Maaf, saya tidak dapat memproses permintaan saat ini. Layanan AI sedang tidak tersedia.",
            "model_provider": "unavailable",
        }


@router.post("/chat/stream")
async def ai_chat_stream(req: ChatRequest):
    messages, provider = await _build_context(req)

    async def event_stream():
        try:
            async for token in llm_service.stream_chat(messages, temperature=0.7, max_tokens=4096):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True, 'provider': provider})}\n\n"
        except Exception as e:
            logger.error(f"AI stream failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/insight")
async def generate_insight(req: InsightRequest):
    try:
        summary = await market_service.get_market_summary()
        indicators = await indicator_service.get_all_indicators()
        headlines = ""
        if req.include_headlines:
            news = await news_service.get_news(limit=10)
            headlines = "; ".join([f"{n['source']}: {n['title']}" for n in news])

        mp = indicators.get("monetary_policy", [])
        bi = next((i for i in mp if i["name"] == "BI-7DRR"), {})
        inf = indicators.get("inflation", [])
        growth = indicators.get("growth", [])

        market_data = {
            "ihsg": summary["ihsg"]["last"],
            "ihsg_change": f"{summary['ihsg']['change_pct']:+.2f}%",
            "usdidr": summary["usdidr"]["last"],
            "bi_rate": f"{summary['bi_rate']}%",
            "sbn_10y": f"{summary['sbn_10y']}%",
            "brent": f"${summary['brent']}",
            "dxy": summary["dxy"],
            "cpi_yoy": f"{inf[0]['value']}%",
            "core_inflation": f"{inf[1]['value']}%",
            "gdp_growth": f"{growth[0]['value']}%",
            "headlines": headlines or "No recent news",
        }
        content = await llm_service.generate_daily_insight(market_data)
        return {"insight": content, "date": __import__("datetime").datetime.now().strftime("%Y-%m-%d"), "model_used": llm_service._provider}
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        return {
            "insight": "Daily insight generation is currently unavailable.",
            "date": __import__("datetime").datetime.now().strftime("%Y-%m-%d"),
            "model_used": "unavailable",
        }
