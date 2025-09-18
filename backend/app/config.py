import os
from pydantic import BaseSettings, Field, AnyUrl
from typing import Optional, List


class Settings(BaseSettings):
    # Core
    APP_NAME: str = "ASM Subdomain Discoverer"
    API_V1_PREFIX: str = "/api/v1"

    # Database and Queue
    DATABASE_URL: str = Field(default="sqlite:///./asm.db")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    RQ_QUEUE_NAME: str = "asm-queue"

    # Security
    ACTIVE_SCAN_TOKEN: Optional[str] = None  # required to enable active bruteforce/resolution
    ALLOW_ORIGINS: List[str] = ["*"]

    # Connectors toggles and API keys
    CHAOS_API_KEY: Optional[str] = None
    SECURITYTRAILS_API_KEY: Optional[str] = None

    # Connector limits
    CONNECTOR_TIMEOUT_SECONDS: int = 20
    CONNECTOR_MAX_CONCURRENCY: int = 10
    RESOLVER_MAX_CONCURRENCY: int = 50
    PER_TARGET_RATE_LIMIT_PER_SEC: float = 10.0

    # Storage for raw connector responses (bonus)
    RAW_STORAGE_DIR: str = "backend/app/storage/raw"

    # Wordlist
    WORDLIST_PATH: str = "wordlists/subdomains.txt"
    BRUTEFORCE_MAX_CANDIDATES: int = 5000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()