"""
Configuration management for the DataViewer application.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "DataViewer"

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: Path = Path("data")
    ALLOWED_EXTENSIONS: set[str] = {".csv"}

    # Database Settings
    SQL_SERVER_DRIVER: str = "ODBC Driver 17 for SQL Server"
    SQL_CONNECTION_TIMEOUT: int = 30
    SQL_QUERY_TIMEOUT: int = 300

    # Data Processing Settings
    MAX_ROWS_PREVIEW: int = 1000
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 10000

    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
