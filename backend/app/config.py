"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://wireuser:devpass@localhost/wire_dev"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    APP_NAME: str = "Wire Management API"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]

    # Feature Flags
    FEATURE_CSV_EXPORT: bool = False
    FEATURE_ADVANCED_FILTERS: bool = True
    FEATURE_AUDIT_LOG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
