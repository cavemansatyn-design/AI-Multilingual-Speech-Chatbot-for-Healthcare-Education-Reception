"""
Application configuration from environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env."""

    app_name: str = Field(default="Multilingual Speech Chatbot", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    # MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db_name: str = Field(default="chatbot_db", alias="MONGODB_DB_NAME")
    # JWT
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    # Optional APIs
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    hf_token: str = Field(default="", alias="HF_TOKEN")
    # Languages
    supported_languages: str = Field(default="en,hi,fr,es,de", alias="SUPPORTED_LANGUAGES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def supported_languages_list(self) -> List[str]:
        return [x.strip() for x in self.supported_languages.split(",") if x.strip()]


def get_settings() -> Settings:
    """Return application settings singleton."""
    return Settings()
