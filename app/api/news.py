from fastapi import APIRouter, Query
from typing import Optional
from app.services.news_service import news_service

router = APIRouter()


@router.get("/")
async def get_news(
    source: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    ticker: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return await news_service.get_news(source, language, ticker, limit, offset)


@router.get("/breaking")
async def get_breaking_news():
    return await news_service.get_breaking_news()


@router.get("/sentiment")
async def get_news_sentiment(days: int = Query(30, ge=1, le=365)):
    return await news_service.get_news_sentiment()


@router.get("/sentiment/history")
async def get_sentiment_history(days: int = Query(30, ge=1, le=365)):
    return await news_service.get_sentiment_history(days)


@router.post("/seed")
async def seed_news():
    await news_service.seed_sample_news()
    return {"status": "ok", "message": "Sample news articles seeded"}
