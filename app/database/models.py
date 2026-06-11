from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    summary = Column(String)
    url = Column(String, unique=True)
    source = Column(String)
    published_at = Column(DateTime)
    language = Column(String, default="id")
    sentiment = Column(Float)
    is_breaking = Column(Boolean, default=False)
    ticker_mentions = Column(JSON)
    tags = Column(JSON)
    body_text = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    snapshot_type = Column(String)
    last_price = Column(Float)
    change = Column(Float)
    change_pct = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_name = Column(String, nullable=False)
    value = Column(Float)
    previous_value = Column(Float)
    change = Column(Float)
    period = Column(String)
    unit = Column(String)
    source = Column(String)
    category = Column(String)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DailyInsight(Base):
    __tablename__ = "daily_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, unique=True)
    content_md = Column(Text)
    model_used = Column(String)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    ticker = Column(String, nullable=False)
    quantity = Column(Float)
    avg_price = Column(Float)
    currency = Column(String, default="IDR")
    opened_at = Column(DateTime)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String)
    symbol = Column(String)
    condition = Column(String)
    threshold = Column(Float)
    keyword = Column(String)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NewsSentimentSnapshot(Base):
    __tablename__ = "news_sentiment_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, unique=True, nullable=False)
    total = Column(Integer, default=0)
    positive = Column(Integer, default=0)
    neutral = Column(Integer, default=0)
    negative = Column(Integer, default=0)
    pct_positive = Column(Float, default=0.0)
    pct_neutral = Column(Float, default=0.0)
    pct_negative = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
