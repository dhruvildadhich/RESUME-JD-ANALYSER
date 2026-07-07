"""
SQLite Cache Service.

Caches Gemini skill extraction payloads, AI explanations, and text embeddings locally to save API quota.
"""
import contextlib
import hashlib
import json
import os
import sqlite3
import time
import re
from typing import Any, List, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".cache"
)
CACHE_DB = os.path.join(CACHE_DIR, "gemini_cache.db")


@contextlib.contextmanager
def get_db_connection():
    """Context manager for thread-safe SQLite connection."""
    conn = sqlite3.connect(CACHE_DB, timeout=30.0)
    try:
        yield conn
    finally:
        conn.close()


def initialize_cache() -> None:
    """Initialize SQLite database and create tables if they do not exist."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at INTEGER
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS explanations (
                    key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    key TEXT PRIMARY KEY,
                    embedding_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if expires_at column exists in extractions table
            cursor.execute("PRAGMA table_info(extractions)")
            columns = [info[1] for info in cursor.fetchall()]
            if "expires_at" not in columns:
                cursor.execute("ALTER TABLE extractions ADD COLUMN expires_at INTEGER")
            
            conn.commit()
        logger.info(f"Local SQLite cache initialized at {CACHE_DB}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite cache: {e}", exc_info=True)


def get_cached_extraction(resume_text: str, jd_text: str, skill_prompt_version: str, model_name: str) -> Optional[dict]:
    """Retrieve a cached extraction result if it exists and is not expired."""
    payload_str = resume_text + jd_text + skill_prompt_version + model_name
    normalized_payload = re.sub(r'\s+', ' ', payload_str.lower().strip())
    key = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
    try:
        if not os.path.exists(CACHE_DB):
            return None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response_json, expires_at FROM extractions WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                res_json, expires_at = row
                if expires_at is not None and time.time() > expires_at:
                    # Expired! Delete it from db
                    cursor.execute("DELETE FROM extractions WHERE key = ?", (key,))
                    conn.commit()
                    return None
                logger.info("Skill extraction loaded from cache")
                return json.loads(res_json)
    except Exception as e:
        logger.warning(f"Failed to read from extraction cache: {e}")
    return None


def set_cached_extraction(resume_text: str, jd_text: str, skill_prompt_version: str, model_name: str, result: dict, ttl_seconds: Optional[int] = None, source: str = "gemini") -> None:
    """Store an extraction result in the cache, optionally with a TTL."""
    payload_str = resume_text + jd_text + skill_prompt_version + model_name
    normalized_payload = re.sub(r'\s+', ' ', payload_str.lower().strip())
    key = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
    try:
        expires_at = int(time.time() + ttl_seconds) if ttl_seconds is not None else None
        os.makedirs(CACHE_DIR, exist_ok=True)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO extractions (key, response_json, expires_at) VALUES (?, ?, ?)",
                (key, json.dumps(result), expires_at)
            )
            conn.commit()
            logger.info(
                "Saved skill extraction result to cache",
                extra={"source": source}
            )
    except Exception as e:
        logger.warning(f"Failed to write to extraction cache: {e}")


def get_cached_explanation(score_result_json: str, extraction_result_json: str) -> Optional[dict]:
    """Retrieve a cached AI explanation if it exists."""
    payload_str = f"{score_result_json}|||{extraction_result_json}"
    normalized_payload = re.sub(r'\s+', ' ', payload_str.lower().strip())
    key = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
    try:
        if not os.path.exists(CACHE_DB):
            return None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response_json FROM explanations WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                logger.info("Cache hit for Gemini AI explanation")
                return json.loads(row[0])
    except Exception as e:
        logger.warning(f"Failed to read from explanation cache: {e}")
    return None


def set_cached_explanation(score_result_json: str, extraction_result_json: str, result: dict) -> None:
    """Store an AI explanation in the cache."""
    payload_str = f"{score_result_json}|||{extraction_result_json}"
    normalized_payload = re.sub(r'\s+', ' ', payload_str.lower().strip())
    key = hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO explanations (key, response_json) VALUES (?, ?)",
                (key, json.dumps(result))
            )
            conn.commit()
            logger.info("Saved Gemini AI explanation to cache")
    except Exception as e:
        logger.warning(f"Failed to write to explanation cache: {e}")


def get_cached_embedding(text: str) -> Optional[List[float]]:
    """Retrieve a cached embedding if it exists."""
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    try:
        if not os.path.exists(CACHE_DB):
            return None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT embedding_json FROM embeddings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                logger.info("Embedding loaded from cache")
                return json.loads(row[0])
    except Exception as e:
        logger.warning(f"Failed to read from embedding cache: {e}")
    return None


def set_cached_embedding(text: str, embedding: List[float]) -> None:
    """Store an embedding in the cache."""
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO embeddings (key, embedding_json) VALUES (?, ?)",
                (key, json.dumps(embedding))
            )
            conn.commit()
            logger.info("Saved text embedding to cache")
    except Exception as e:
        logger.warning(f"Failed to write to embedding cache: {e}")
