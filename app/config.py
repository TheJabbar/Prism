from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False
    app_secret_key: str = "change-me"

    database_url: str = "sqlite+aiosqlite:///./data/prism.db"

    llm_provider: str = "openrouter"
    llm_model: str = "openrouter:anthropic/claude-sonnet-4"

    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    groq_api_key: Optional[str] = None
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "groq:mixtral-8x7b-32768"

    tz: str = "Asia/Jakarta"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
