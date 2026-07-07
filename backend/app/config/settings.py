"""
Application settings using pydantic-settings.
All configuration is read from environment variables / .env file.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Gemini ──────────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # Keep for backward compatibility
    
    gemini_extraction_model: str = "gemini-2.5-flash-lite"
    gemini_explanation_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    # ── Embedding ────────────────────────────────────────────────────────────
    embedding_provider: str = "local"
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # ── Scoring weights ──────────────────────────────────────────────────────
    skill_weight: float = 0.60
    semantic_weight: float = 0.40

    # ── Server / CORS ─────────────────────────────────────────────────────────
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    log_level: str = "INFO"

    # ── Token limits ──────────────────────────────────────────────────────────
    gemini_resume_token_limit: int = 6000
    gemini_jd_token_limit: int = 3000

    # ── Limits ───────────────────────────────────────────────────────────────
    max_pdf_size_mb: int = 10


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton)."""
    return Settings()
