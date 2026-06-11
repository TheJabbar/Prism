# PRISM — Portfolio Research & Investment Strategy Monitor

**Indonesia's Financial Pulse. All in One Terminal.**

PRISM is a self-hosted Indonesian financial intelligence terminal that aggregates real-time market data, macroeconomic indicators, news sentiment analysis, and AI-powered market insights into a unified web dashboard.

```mermaid
graph TB
    subgraph User["User Layer"]
        Browser["Web Browser"]
    end

    subgraph Frontend["Frontend Layer"]
        HTML["index.html<br/>Jinja2 Template"]
        CSS["prism.css<br/>Dark Luxe Theme"]
        JS["app.js<br/>Vanilla JS + Chart.js"]
    end

    subgraph API["API Layer — FastAPI"]
        Router["/api/v1 Router"]
        MarketAPI["Market Routes"]
        NewsAPI["News Routes"]
        IndicatorsAPI["Indicators Routes"]
        IDXAPI["IDX Routes"]
        AIAPI["AI Analyst Routes"]
        BondsAPI["Bonds Routes"]
        FXAPI["FX Routes"]
        PortfolioAPI["Portfolio Routes"]
        AlertsAPI["Alerts Routes"]
        TickersAPI["Tickers Routes"]
        ExportAPI["Export Routes"]
    end

    subgraph Services["Service Layer"]
        MarketSvc["Market Service"]
        NewsSvc["News Service"]
        IndicatorSvc["Indicator Service"]
        IDXSvc["IDX Service"]
        LLMSvc["LLM Service<br/>OpenRouter + Groq"]
        CacheSvc["Memory Cache Service"]
    end

    subgraph Scrapers["Data Scrapers"]
        Yahoo["Yahoo Finance<br/>yfinance"]
        BIScraper["BI Rate Scraper"]
        CNBC["News Scrapers<br/>CNBC / Kontan / Bisnis"]
        IDXClient["IDX Client<br/>idx.co.id"]
    end

    subgraph Database["Database Layer"]
        SQLite[(SQLite<br/>prism.db)]
        Models["SQLAlchemy Models<br/>8 tables"]
    end

    subgraph External["External APIs"]
        OpenRouter["OpenRouter API<br/>(Primary LLM)"]
        Groq["Groq API<br/>(Fallback LLM)"]
        YahooFinance["Yahoo Finance"]
        IDX["IDX.co.id"]
        BI["bi.go.id"]
        NewsSources["CNBC Indonesia<br/>Kontan<br/>Bisnis.com"]
    end

    Browser --> HTML
    HTML --> JS
    JS --> Router
    Router --> MarketAPI & NewsAPI & IndicatorsAPI & IDXAPI & AIAPI & BondsAPI & FXAPI & PortfolioAPI & AlertsAPI & TickersAPI & ExportAPI
    MarketAPI --> MarketSvc
    NewsAPI --> NewsSvc
    IndicatorsAPI --> IndicatorSvc
    IDXAPI --> IDXSvc
    AIAPI --> LLMSvc
    MarketSvc --> Yahoo
    NewsSvc --> CNBC
    IndicatorSvc --> BIScraper
    IDXSvc --> IDXClient
    LLMSvc --> OpenRouter
    LLMSvc --> Groq
    Yahoo --> YahooFinance
    CNBC --> NewsSources
    BIScraper --> BI
    IDXClient --> IDX
    MarketSvc --> CacheSvc
    NewsSvc --> CacheSvc
    MarketSvc --> Database
    NewsSvc --> Database
    IndicatorSvc --> Database
    Database --> Models
    Models --> SQLite
```

---

## Features

- **Real-time Market Data** — IHSG, LQ45, USD/IDR, DXY, Brent Crude, Gold via Yahoo Finance
- **IDX Integration** — All 44 IDX indices, stock screener (957+ stocks with PER/PBV/ROA/ROE), trade summary, company profiles, financial ratios
- **BI Rate Tracking** — Verified BI-7DRR history with 30-month timeline, scraped from bi.go.id
- **Macroeconomic Indicators** — Inflation (CPI), GDP growth, trade balance, banking metrics, fiscal data
- **News Aggregation** — Scraped from CNBC Indonesia, Kontan, Bisnis.com with LLM-based sentiment classification
- **AI Analyst** — Streaming chat with OpenRouter (primary) + Groq (fallback) LLMs, context-aware with real market data
- **Fixed Income** — Yield curve, benchmark bonds, CDS spreads
- **Forex** — Major pair rates + BI JISDOR
- **Portfolio Tracking** — Demo portfolio with cost basis, P&L, and holdings
- **Custom Alerts** — Price and news keyword alerts
- **Ticker Management** — Add, delete, refresh individual tickers
- **Export** — CSV and JSON export of all data

---

## Tech Stack

```mermaid
graph LR
    subgraph Backend
        FastAPI[FastAPI]
        SQLAlchemy[SQLAlchemy Async]
        SQLite[(SQLite)]
        APScheduler[APScheduler]
    end
    subgraph Frontend
        Jinja2[Jinja2 Templates]
        VanillaJS[Vanilla JS]
        ChartJS[Chart.js]
        MarkedJS[Marked.js]
    end
    subgraph Infrastructure
        Docker[Docker / Podman]
        UV[UV Package Manager]
    end
    subgraph Data
        YFinance[Yahoo Finance]
        IDXScraper[IDX.co.id]
        NewsScraper[News Scrapers]
    end
    subgraph AI
        OpenRouter[OpenRouter API]
        Groq[Groq API]
    end

    FastAPI --> SQLAlchemy
    SQLAlchemy --> SQLite
    FastAPI --> APScheduler
    Jinja2 --> VanillaJS
    VanillaJS --> ChartJS
    VanillaJS --> MarkedJS
    FastAPI --> Jinja2
    YFinance --> FastAPI
    IDXScraper --> FastAPI
    NewsScraper --> FastAPI
    OpenRouter --> FastAPI
    Groq --> FastAPI
    Docker --> FastAPI
    UV --> FastAPI
```

| Category | Technology |
|---|---|
| **Language** | Python 3.11+ |
| **Web Framework** | FastAPI (async) |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | SQLite (default), PostgreSQL-ready |
| **Template Engine** | Jinja2 |
| **Frontend** | Vanilla JavaScript, CSS3 |
| **Charts** | Chart.js 4.x |
| **Markdown** | Marked.js |
| **LLM** | OpenRouter (primary) + Groq (fallback) |
| **Market Data** | yfinance |
| **News Scraping** | scrapling |
| **Task Scheduler** | APScheduler |
| **Package Manager** | UV |
| **Container** | Docker / Podman |
| **CI** | podman-compose |

---

## Quick Start

### Prerequisites

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) package manager
- OpenRouter API key (or Groq API key)

### Local Development

```bash
# Clone and enter the project
cd prism

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run the development server
uv run uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

### Docker / Podman

```bash
# Build and start
podman-compose up -d

# Or with Docker Compose
docker compose up -d
```

### Configuration

Create a `.env` file:

```env
# LLM Configuration (at least one required)
OPENROUTER_API_KEY=sk-or-v1-your-key
GROQ_API_KEY=gsk_your-key
LLM_PROVIDER=openrouter    # or "groq"

# Optional
DATABASE_URL=sqlite+aiosqlite:///./data/prism.db
```

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

```mermaid
graph TD
    subgraph Market
        MS["GET /market/summary"]
        MSnap["GET /market/snapshots"]
        MI["GET /market/indicators"]
    end
    subgraph "IDX (Indonesia Stock Exchange)"
        IO["GET /idx/overview"]
        II["GET /idx/indices"]
        IIC["GET /idx/indices/{code}/chart"]
        ITS["GET /idx/trade-summary"]
        ITG["GET /idx/top-gainers"]
        ITL["GET /idx/top-losers"]
        ISS["GET /idx/stocks"]
        ISSC["GET /idx/stocks/{code}"]
        IScr["GET /idx/screener"]
        IFR["GET /idx/financial-ratios"]
        ICP["GET /idx/companies"]
        ICC["GET /idx/companies/{code}"]
    end
    subgraph News
        NG["GET /news"]
        NB["GET /news/breaking"]
        NS["GET /news/sentiment"]
        NSH["GET /news/sentiment/history"]
        NSeed["POST /news/seed"]
    end
    subgraph Indicators
        IM["GET /indicators/macro"]
        IG["GET /indicators/global"]
    end
    subgraph "AI Analyst"
        AC["POST /ai/chat"]
        ACS["POST /ai/chat/stream"]
        AI["POST /ai/insight"]
    end
    subgraph Bonds
        BYC["GET /bonds/yield-curve"]
        BB["GET /bonds/benchmarks"]
        BCDS["GET /bonds/cds"]
        BA["GET /bonds/auctions"]
    end
    subgraph FX
        FR["GET /fx/rates"]
        FJ["GET /fx/jisdor"]
        FD["GET /fx/dxy"]
    end
    subgraph Portfolio
        PG["GET /portfolio"]
        PD["GET /portfolio/demo"]
        PP["POST /portfolio"]
        PH["POST /portfolio/holdings"]
    end
    subgraph Alerts
        AG["GET /alerts"]
        AP["POST /alerts"]
        AD["DELETE /alerts/{id}"]
    end
    subgraph Tickers
        TG["GET /tickers"]
        TS["GET /tickers/{symbol}"]
        TP["POST /tickers"]
        TD["DELETE /tickers/{symbol}"]
        TSeed["POST /tickers/seed"]
        TR["POST /tickers/refresh"]
    end
    subgraph System
        ExpCSV["GET /export/csv"]
        ExpJSON["GET /export/json"]
        Health["GET /health"]
        Ready["GET /ready"]
    end
```

---

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant FastAPI
    participant Scraper
    participant LLM
    participant DB

    User->>Browser: Click Markets tab
    Browser->>FastAPI: GET /api/v1/market/summary
    FastAPI->>Scraper: fetch_market_summary()
    Scraper->>Yahoo Finance: Fetch ticker data
    Scraper->>Yahoo Finance: Fetch 1mo history (per ticker)
    Yahoo Finance-->>Scraper: Price + history data
    Scraper-->>FastAPI: Structured data with history
    FastAPI-->>Browser: JSON response
    Browser->>Browser: Render indicator grid with clickable cards
    User->>Browser: Click IHSG card
    Browser->>Browser: Create floating 260x160 Chart.js popup

    User->>Browser: Click AI Analyst tab
    Browser->>FastAPI: POST /api/v1/ai/chat/stream
    FastAPI->>LLM: OpenRouter (or Groq fallback)
    FastAPI->>Scraper: Fetch latest market data for context
    LLM-->>FastAPI: Streaming tokens
    FastAPI-->>Browser: SSE (text/event-stream)
    Browser->>Browser: Render Markdown via marked.js

    User->>Browser: Click News tab
    Browser->>FastAPI: GET /api/v1/news/
    FastAPI->>Scraper: scrape_cnbc(), scrape_kontan(), scrape_bisnis()
    Scraper-->>FastAPI: Raw articles
    FastAPI->>LLM: Classify sentiment (batches of 20)
    LLM-->>FastAPI: Sentiment scores
    FastAPI->>DB: Store articles + scores
    DB-->>FastAPI: Confirm
    FastAPI-->>Browser: Articles with sentiment
```

---

## Architecture

### Backend Structure

```
app/
├── main.py                  # FastAPI app entry, lifespan, static mounts
├── config.py                # Pydantic settings (.env)
├── api/                     # Route handlers
│   ├── router.py            # Central router mounting all sub-routers
│   ├── market.py            # Market summary, snapshots
│   ├── news.py              # News feed, sentiment
│   ├── indicators.py        # Macro & global indicators
│   ├── idx.py               # IDX stock exchange data
│   ├── bonds.py             # Fixed income
│   ├── fx.py                # Forex
│   ├── portfolio.py         # Portfolio management
│   ├── ai_analyst.py        # AI chat + streaming
│   ├── alerts.py            # Custom alerts
│   ├── tickers.py           # Ticker CRUD
│   └── export.py            # CSV/JSON export
├── scrapers/
│   ├── market/
│   │   ├── yahoo_fetcher.py # Yahoo Finance integration
│   │   └── bi_scraper.py    # Bank Indonesia rate scraper
│   ├── news/
│   │   └── cnbc_scraper.py  # CNBC/Kontan/Bisnis scraper
│   └── idx/
│       ├── idx_client.py    # IDX HTTP client (cookies, retry)
│       ├── market.py        # IDX indices & trade summary
│       ├── trading.py       # IDX stock summary & trades
│       └── company.py       # IDX company profiles & screener
├── services/
│   ├── market_service.py    # Market orchestration
│   ├── news_service.py      # News + sentiment orchestration
│   ├── idx_service.py       # IDX data orchestration
│   ├── indicator_service.py # Macro indicators
│   ├── llm_service.py       # OpenRouter + Groq LLM client
│   └── cache_service.py     # In-memory TTL cache
├── database/
│   ├── models.py            # 8 SQLAlchemy models
│   └── session.py           # Async session factory
├── utils/
│   ├── logger.py            # Loguru configuration
│   └── formatters.py        # Number/currency formatters
├── static/
│   ├── css/prism.css        # Dark Luxe theme (1179 lines)
│   └── js/app.js            # Frontend logic (919 lines)
└── templates/
    └── index.html           # Single-page application shell
```

### Database Schema

```mermaid
erDiagram
    NewsArticle {
        str id PK
        str title
        str summary
        str url UNIQUE
        str source
        datetime published_at
        str language
        float sentiment
        bool is_breaking
        json ticker_mentions
        json tags
        datetime created_at
    }

    MarketSnapshot {
        int id PK
        str symbol
        str snapshot_type
        float last_price
        float change
        float change_pct
        float volume
        datetime timestamp
    }

    MacroIndicator {
        int id PK
        str indicator_name
        float value
        float previous_value
        float change
        str period
        str unit
        str source
        str category
        date published_at
        datetime created_at
    }

    DailyInsight {
        int id PK
        date date UNIQUE
        text content_md
        str model_used
        datetime generated_at
    }

    Portfolio {
        int id PK
        str name
        datetime created_at
    }

    Holding {
        int id PK
        int portfolio_id FK
        str ticker
        float quantity
        float avg_price
        str currency
        datetime opened_at
    }

    Alert {
        int id PK
        str alert_type
        str symbol
        str condition
        float threshold
        str keyword
        bool is_active
        datetime triggered_at
        datetime created_at
    }

    NewsSentimentSnapshot {
        int id PK
        date date UNIQUE
        int total
        int positive
        int neutral
        int negative
        float pct_positive
        float pct_neutral
        float pct_negative
        float score
        datetime created_at
    }

    Portfolio ||--o{ Holding : contains
```

---

## LLM Sentiment Classification

News sentiment is classified using LLM (not keyword matching) for accurate context-aware analysis. For example, *"IHSG naik"* is positive but *"Pertamax naik"* is negative.

```mermaid
flowchart LR
    A["Scraped Articles"] --> B{Has sentiment?}
    B -->|Yes| C["Skip (cached)"]
    B -->|No| D["Batch 20 articles"]
    D --> E["LLM Classify<br/>OpenRouter / Groq"]
    E --> F{"Valid JSON?"}
    F -->|Yes| G["Save scores to DB"]
    F -->|No| H["Retry individual"]
    H --> I["Default to neutral"]
    G --> J["Daily snapshot<br/>aggregation"]
    J --> K["14-day sentiment<br/>history chart"]
```

---

## Deployment

### Production Build

```bash
# Build with podman
podman-compose build

# Run
podman-compose up -d

# View logs
podman logs -f prism-terminal

# Stop
podman-compose down
```

### Container Details

- **Base image**: `python:3.11-slim` (two-stage build)
- **Builder**: `ghcr.io/astral-sh/uv:latest`
- **Port**: 8000
- **Healthcheck**: `GET /health` every 15s
- **Volumes**:
  - `db_data:/app/data` — SQLite database persistence
  - `./logs:/app/logs` — Application logs
  - `./exports:/app/exports` — CSV/JSON exports
  - `./.env:/app/.env:ro` — Environment configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENROUTER_API_KEY` | Yes* | — | OpenRouter API key (primary LLM) |
| `GROQ_API_KEY` | Yes* | — | Groq API key (fallback LLM) |
| `LLM_PROVIDER` | No | `openrouter` | Active LLM provider |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./data/prism.db` | Database connection string |
| `TZ` | No | `Asia/Jakarta` | Timezone |

*\*At least one LLM API key is required.*

---

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Specific module
uv run pytest tests/test_api_market.py -v

# With coverage
uv run pytest --cov=app
```

### Adding a New Data Source

1. Create a scraper in `app/scrapers/` (follow existing patterns)
2. Add a service method in `app/services/`
3. Add API routes in `app/api/`
4. Register in `app/api/router.py`
5. Add frontend rendering in `app/static/js/app.js`
6. Write tests in `tests/`

---

## License

MIT
