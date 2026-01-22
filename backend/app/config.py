from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic Settings.
    Loads configuration from environment variables with strong typing.
    """
    # MongoDB Configuration
    MONGODB_URL: str

    # Redis Configuration
    REDIS_URL: str

    # Google Services
    GOOGLE_PLACES_API_KEY: str
    PAGESPEED_API_KEY: str

    # OpenAI Configuration
    OPENAI_API_KEY: str

    # Resend Email Service
    RESEND_API_KEY: str

    # Cloudflare R2 Storage
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str

    # Frontend URL for CORS
    FRONTEND_URL: str

    # Environment Configuration
    ENVIRONMENT: Literal['development', 'staging', 'production'] = 'development'

    # Logging Configuration
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'

    # Celery Configuration
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Optional: Additional Security Settings
    SECRET_KEY: str

    # Model configuration to load from .env file
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

# Create a singleton settings instance
settings = Settings()