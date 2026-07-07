"""
Reranker Service using Cross-Encoder.
"""

import numpy as np
from sentence_transformers import CrossEncoder
from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_reranker: CrossEncoder | None = None

def get_reranker() -> CrossEncoder:
    """
    Return cached CrossEncoder model.
    """
    global _reranker
    if _reranker is None:
        settings = get_settings()
        logger.info(f"Loading local CrossEncoder model: {settings.reranker_model}")
        _reranker = CrossEncoder(settings.reranker_model)
    return _reranker

def validate_match(jd_requirement: str, resume_evidence: str) -> float:
    """
    Validates if the resume evidence satisfies the JD requirement using a cross-encoder.
    Returns a probability between 0.0 and 1.0.
    """
    if not jd_requirement.strip() or not resume_evidence.strip():
        return 0.0
        
    try:
        model = get_reranker()
        # predict takes a list of sentence pairs
        score = model.predict([(jd_requirement, resume_evidence)])[0]
        # ms-marco models typically output logits, so we apply a sigmoid function
        prob = 1.0 / (1.0 + np.exp(-score))
        return float(prob)
    except Exception as exc:
        logger.error(f"Reranker failed: {exc}", exc_info=True)
        return 0.5 # Default fallback
