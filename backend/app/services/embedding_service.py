"""
Embedding Service.

Uses Gemini embedding model for semantic similarity.
"""

import numpy as np
from google import genai

from app.config.settings import get_settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger
from app.core.cache import get_cached_embedding, set_cached_embedding
from google.genai.errors import ClientError, ServerError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import httpx
import requests

logger = get_logger(__name__)


_client: genai.Client | None = None


def get_embedding_model() -> genai.Client:
    """
    Return cached Gemini client.
    """
    global _client

    if _client is None:
        settings = get_settings()

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

        logger.info("Gemini embedding client loaded")

    return _client


def get_embedding(text: str) -> np.ndarray:
    """
    Generate Gemini embedding.
    """
    settings = get_settings()
    cached_val = get_cached_embedding(text)
    if cached_val is not None:
        return np.array(cached_val)

    logger.info("Cache miss. Calling Gemini")

    def should_retry(exception):
        # Do not retry ClientErrors (4xx), such as 429 quota exceeded, 401/403 auth, 404, etc.
        if isinstance(exception, ClientError):
            return False
        # Retry ServerErrors (5xx)
        if isinstance(exception, ServerError):
            return True
        # Retry APIErrors with code >= 500
        if isinstance(exception, APIError):
            code = getattr(exception, "code", None)
            if code is not None and isinstance(code, int):
                return code >= 500
            return True
        # Retry timeouts and connection errors
        if isinstance(exception, (httpx.TimeoutException, httpx.ConnectError, requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
            return True
        # Retry other potential network/timeout errors
        exc_name = type(exception).__name__
        if "timeout" in exc_name.lower() or "connect" in exc_name.lower():
            return True
        return False

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(should_retry),
    )
    def _embed_with_retry():
        logger.info(f"Calling Gemini API ({settings.gemini_embedding_model}) for text embedding")
        client = get_embedding_model()
        return client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=text,
        )

    result = _embed_with_retry()
    values = result.embeddings[0].values
    set_cached_embedding(text, values)

    return np.array(values)


def get_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Compute cosine similarity.
    """

    try:
        embedding_a = get_embedding(text_a)
        embedding_b = get_embedding(text_b)

        similarity = float(
            np.dot(
                embedding_a,
                embedding_b,
            )
            /
            (
                np.linalg.norm(embedding_a)
                *
                np.linalg.norm(embedding_b)
            )
        )

        return max(
            0.0,
            min(
                1.0,
                similarity,
            ),
        )

    except Exception as exc:
        logger.error(
            "Embedding failed",
            extra={
                "error": str(exc),
            },
        )

        raise EmbeddingError(
            f"Embedding failed: {exc}"
        ) from exc