"""
API Gateway Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # API Gateway
    app_name: str = "LocalDBKit API Gateway"
    app_version: str = "0.3.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    jwt_secret_key: str = "your-secret-key-change-in-production-please"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # Rate Limiting
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    rate_limit_default: str = "60/minute"
    rate_limit_auth: str = "5/minute"
    rate_limit_llm: str = "10/minute"

    # Backend Services
    postgres_url: str = "postgresql://postgres:postgres@postgres:5432/mydb"
    mongodb_url: str = "mongodb://admin:admin@mongodb:27017"
    redis_url: str = "redis://redis:6379"
    ollama_url: str = "http://ollama:11434"
    qdrant_url: str = "http://qdrant:6333"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",
    ]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
