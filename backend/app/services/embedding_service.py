"""
Embedding Service.

Uses Gemini embedding model for semantic similarity.
"""

import re
import numpy as np
from google import genai

from app.config.settings import get_settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger
from app.core.cache import get_cached_embedding, set_cached_embedding
from app.services.document_analyzer import parse_resume_sections, parse_jd_sections
from google.genai.errors import ClientError, ServerError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import httpx
import requests
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)

_client: genai.Client | None = None

class EmbeddingService:
    _model: SentenceTransformer | None = None

    @classmethod
    async def warmup(cls):
        """Load the model into memory during startup."""
        if cls._model is None:
            settings = get_settings()
            if settings.embedding_provider == "local":
                logger.info(f"Loading local SentenceTransformer model: {settings.embedding_model}")
                cls._model = SentenceTransformer(settings.embedding_model)

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Return the pre-loaded model or load it if not available (fallback)."""
        if cls._model is None:
            settings = get_settings()
            logger.info(f"Loading local SentenceTransformer model: {settings.embedding_model} (Sync fallback)")
            cls._model = SentenceTransformer(settings.embedding_model)
        return cls._model

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

def get_bge_model() -> SentenceTransformer:
    """
    Return cached SentenceTransformer model using Singleton.
    """
    return EmbeddingService.get_model()


def get_embedding(text: str, prefix: str = "") -> np.ndarray:
    """
    Generate Gemini or local embedding.
    """
    settings = get_settings()
    
    full_text = f"{prefix}{text}"
    
    cached_val = get_cached_embedding(full_text)
    if cached_val is not None:
        return np.array(cached_val)

    if settings.embedding_provider == "local":
        # Handle empty text
        if not text.strip():
            # return zero vector
            return np.zeros(768) # default bge-base dim
            
        model = get_bge_model()
        # normalize_embeddings=True ensures cosine similarity is just dot product
        # but we also have our compute_cosine_sim that normalizes
        emb = model.encode(full_text, normalize_embeddings=True)
        # cache it
        set_cached_embedding(full_text, emb.tolist())
        return emb

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
            contents=full_text,
        )

    result = _embed_with_retry()
    values = result.embeddings[0].values
    set_cached_embedding(full_text, values)

    return np.array(values)


def _compute_cosine_sim(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(embedding_a)
    norm_b = np.linalg.norm(embedding_b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    similarity = float(np.dot(embedding_a, embedding_b) / (norm_a * norm_b))
    return max(0.0, min(1.0, similarity))

def get_similarity(
    text_a: str,
    text_b: str,
) -> dict:
    """
    Compute section-aware semantic cosine similarity using strict weighted chunks:
    Technical Skill Similarity (50%)
    Project Similarity (30%)
    Experience Similarity (20%)
    """

    try:
        resume_prefix = "Represent this candidate resume for job matching: "
        jd_prefix = "Represent this job description for candidate matching: "
        
        resume_sections = parse_resume_sections(text_a)
        jd_sections = parse_jd_sections(text_b)
        
        # If parsing yields only general text, fallback to global similarity
        if len(resume_sections) <= 1 and len(jd_sections) <= 1:
            emb_a = get_embedding(text_a, prefix=resume_prefix)
            emb_b = get_embedding(text_b, prefix=jd_prefix)
            final_sim = _compute_cosine_sim(emb_a, emb_b)
            return {
                "skill_semantic_score": final_sim,
                "project_semantic_score": final_sim,
                "experience_semantic_score": final_sim,
                "final_semantic_score": final_sim
            }
            
        scores = []
        weights = []
        
        result_dict = {
            "skill_semantic_score": 0.0,
            "project_semantic_score": 0.0,
            "experience_semantic_score": 0.0,
            "final_semantic_score": 0.0
        }
        
        # 1. Technical Skill Similarity (50% weight)
        resume_skills = resume_sections.get("skills", "") + " " + resume_sections.get("certifications", "") + " " + resume_sections.get("general", "")
        jd_skills = jd_sections.get("skills", "") + " " + jd_sections.get("qualifications", "") + " " + jd_sections.get("general", "")
        
        if resume_skills.strip() and jd_skills.strip():
            sim = _compute_cosine_sim(get_embedding(resume_skills, prefix=resume_prefix), get_embedding(jd_skills, prefix=jd_prefix))
            scores.append(sim)
            weights.append(0.50)
            result_dict["skill_semantic_score"] = sim
            
        # 2. Project Similarity (30% weight)
        resume_proj = resume_sections.get("projects", "")
        jd_resp = jd_sections.get("responsibilities", "")
        
        if resume_proj.strip() and jd_resp.strip():
            sim = _compute_cosine_sim(get_embedding(resume_proj, prefix=resume_prefix), get_embedding(jd_resp, prefix=jd_prefix))
            scores.append(sim)
            weights.append(0.30)
            result_dict["project_semantic_score"] = sim
            
        # 3. Experience Similarity (20% weight)
        resume_exp = resume_sections.get("experience", "")
        jd_exp = jd_sections.get("experience_requirements", "")
        
        if resume_exp.strip() and jd_exp.strip():
            sim = _compute_cosine_sim(get_embedding(resume_exp, prefix=resume_prefix), get_embedding(jd_exp, prefix=jd_prefix))
            scores.append(sim)
            weights.append(0.20)
            result_dict["experience_semantic_score"] = sim
            
        if not scores:
            # Fallback
            emb_a = get_embedding(text_a, prefix=resume_prefix)
            emb_b = get_embedding(text_b, prefix=jd_prefix)
            final_sim = _compute_cosine_sim(emb_a, emb_b)
            return {
                "skill_semantic_score": final_sim,
                "project_semantic_score": final_sim,
                "experience_semantic_score": final_sim,
                "final_semantic_score": final_sim
            }
            
        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        result_dict["final_semantic_score"] = max(0.0, min(1.0, weighted_score))
        return result_dict

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