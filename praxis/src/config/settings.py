"""
Configuration settings for Praxis v0.3 MVP

Decisions made per §16:
- Autonomy level default: 1 (supervised execution)
- KnowledgeBase: empty at start, manually populated
- Traceability: present but non-blocking in MVP
- Job queue: synchronous processing for Phase 2
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Praxis"
    APP_VERSION: str = "0.3.0-mvp"
    DEBUG: bool = True
    
    # Database - SQLite for MVP, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./praxis.db"
    # For production: DATABASE_URL = "postgresql://user:pass@localhost:5432/praxis"
    
    # File storage
    STORAGE_PATH: str = "./storage/artifacts"
    MAX_FILE_SIZE_MB: int = 50
    
    # AI/LLM configuration
    LLM_PROVIDER: str = "openai"  # openai, anthropic, or local
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    
    # Autonomy settings (§4)
    DEFAULT_AUTONOMY_LEVEL: int = 1  # Level 1: supervised execution
    
    # Readiness thresholds (§3.3)
    DEFAULT_READINESS_THRESHOLD: float = 0.75
    CRITICAL_DIMENSION_THRESHOLD: float = 0.50
    
    # Learning settings (§3.7)
    LEARNING_ENABLED: bool = True
    AUTO_ADAPT_ENABLED: bool = False  # Disabled for MVP, requires explicit validation
    
    # Error recovery (§3.16)
    MAX_RETRY_ATTEMPTS: int = 3
    ERROR_ESCALATION_ENABLED: bool = True
    
    # Traceability (§3.13)
    TRACEABILITY_REQUIRED: bool = False  # Non-blocking for MVP
    TRACEABILITY_WARNING_ENABLED: bool = True
    
    # Metrics (§14)
    METRICS_ENABLED: bool = True
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ENCRYPTION_ENABLED: bool = False  # Can be enabled for sensitive data
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
