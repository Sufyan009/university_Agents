"""Application configuration settings."""
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(str(_API_DIR / ".env"), str(_API_DIR / ".env.local")),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Configuration
    app_name: str = Field(default="University Agent API", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")

    # Database Configuration
    database_url: str = Field(alias="DATABASE_URL")

    # JWT Configuration
    jwt_secret_key: str = Field(default="change-me-jwt", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=1440,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # File Upload Configuration
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, alias="MAX_FILE_SIZE")  # 10MB

    # CORS Configuration
    allowed_origins: str = Field(
        default="*",
        alias="ALLOWED_ORIGINS"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # LiveKit Configuration
    livekit_api_key: Optional[str] = Field(default=None, alias="LIVEKIT_API_KEY")
    livekit_api_secret: Optional[str] = Field(default=None, alias="LIVEKIT_API_SECRET")

    # Agent internal API key — shared secret for agent→API call tracking
    agent_internal_api_key: str = Field(default="", alias="AGENT_INTERNAL_API_KEY")

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
