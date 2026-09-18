"""
AME - Configuração Central
Pydantic Settings com validação e defaults seguros
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List

class Settings(BaseSettings):
    # Core
    ame_env: str = Field(default="development", env="AME_ENV")
    ame_secret_key: str = Field(default="change-me-32-chars-ame-secret-key!!", env="AME_SECRET_KEY")
    ame_debug: bool = Field(default=True, env="AME_DEBUG")
    database_url: str = Field(default="sqlite:///./ame.db", env="DATABASE_URL")
    
    # Security
    jwt_secret: str = Field(default="change-me-jwt-secret-32-chars-ame!!", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, env="JWT_EXPIRE_MINUTES")
    api_rate_limit: int = Field(default=100, env="API_RATE_LIMIT")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000,http://localhost:8001", env="CORS_ORIGINS")
    
    # LLM Router
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    tavily_api_key: Optional[str] = Field(default=None, env="TAVILY_API_KEY")
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")
    research_provider: str = Field(default="tavily", env="AME_RESEARCH_PROVIDER")
    allow_mocks: bool = Field(default=True, env="AME_ALLOW_MOCKS")
    real_execution: bool = Field(default=False, env="AME_REAL_EXECUTION")
    max_daily_ai_cost_usd: float = Field(default=10.0, env="AME_MAX_DAILY_AI_COST_USD")
    default_cheap_model: str = Field(default="gpt-4o-mini", env="AME_DEFAULT_CHEAP_MODEL")
    default_power_model: str = Field(default="gpt-4o", env="AME_DEFAULT_POWER_MODEL")
    default_fast_model: str = Field(default="gemini-1.5-flash", env="AME_DEFAULT_FAST_MODEL")
    
    # Finance
    initial_balance: float = Field(default=1000.0, env="AME_INITIAL_BALANCE")
    burn_rate_daily: float = Field(default=5.0, env="AME_BURN_RATE_DAILY")
    survival_threshold_days: int = Field(default=7, env="AME_SURVIVAL_THRESHOLD_DAYS")
    emergency_threshold_days: int = Field(default=3, env="AME_EMERGENCY_THRESHOLD_DAYS")
    
    # Observability
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    worker_poll_seconds: float = Field(default=2.0, env="AME_WORKER_POLL_SECONDS")
    worker_batch_size: int = Field(default=5, env="AME_WORKER_BATCH_SIZE")
    
    # System
    tz: str = Field(default="America/Sao_Paulo", env="TZ")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ame_env.lower() == "production"

    @property
    def mocks_enabled(self) -> bool:
        """Mocks are allowed only outside real execution / production by explicit opt-in."""
        return bool(self.allow_mocks and not self.real_execution and not self.is_production)

    @property
    def database_url_async(self) -> str:
        # Converte sqlite para aiosqlite async
        if self.database_url.startswith("sqlite:///"):
            return self.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
