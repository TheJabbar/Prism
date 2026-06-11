from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime, timezone

from app.api.router import api_router
from app.database.session import engine
from app.database.models import Base
from app.config import settings
from app.utils.logger import logger

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PRISM Terminal...")
    data_dir = Path(settings.database_url.replace("sqlite+aiosqlite:///", "")).parent
    data_dir.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import text
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [r[0] for r in result.fetchall()]
        logger.info(f"Database tables: {tables} at {settings.database_url}")

    from app.services.news_service import news_service
    try:
        await news_service.seed_scraped_news()
        logger.info("News seeding complete")
    except Exception as e:
        logger.warning(f"News seeding failed: {e}")

    yield
    await engine.dispose()
    logger.info("PRISM Terminal stopped.")


app = FastAPI(
    title="PRISM - Portfolio Research & Investment Strategy Monitor",
    description="Indonesian Financial Intelligence Terminal",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": "prism",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
async def readiness():
    try:
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {
        "status": "ready" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
