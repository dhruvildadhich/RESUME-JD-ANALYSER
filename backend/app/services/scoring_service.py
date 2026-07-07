"""
Scoring Service.

Computes a rich weighted match score based on 4 components:
  - 40% Technical Skill Match (evidence-weighted — prevents keyword stuffing)
  - 25% AI Engineering Depth (project evidence with action verbs)
  - 20% Semantic Similarity (content embeddings)
  - 15% Production Engineering (bonus & evidence quality)

Evidence levels for each matched skill:
  - MENTIONED  (generic/no evidence)      → 0.40 multiplier
  - USED       (project context present)   → 0.75 multiplier
  - BUILT/OWNED (action verb + ownership) → 1.00 multiplier
"""
import re
from typing import List, Optional

from app.core.constants import (
    IMPORTANCE_CRITICAL,
    IMPORTANCE_IMPORTANT,
    IMPORTANCE_OPTIONAL,
    IMPORTANCE_WEIGHTS,
    MATCH_TYPE_WEIGHTS,
    EVIDENCE_MENTIONED_SCORE,
    EVIDENCE_USED_SCORE,
    EVIDENCE_BUILT_DEPLOYED_SCORE,
    WEIGHT_TECH_SKILL,
    WEIGHT_PROJECT_EXP,
    WEIGHT_SEMANTIC,
    WEIGHT_PRODUCTION,
    PROJECT_SCORE_BUILT_AT_SCALE,
    PROJECT_SCORE_BUILT,
    PROJECT_SCORE_MIXED,
    PROJECT_SCORE_LEARNING,
    PROJECT_SCORE_CONTEXT,
    PROJECT_SCORE_MINIMAL,
    PROJECT_SCORE_NORMALIZATION_DIVISOR,
    PROD_BONUS_DOCKER,
    PROD_BONUS_DOCKER_EVIDENCE,
    PROD_BONUS_API,
    PROD_BONUS_DATABASE,
    PROD_BONUS_TESTING,
    PROD_BONUS_CLOUD,
    PROD_BONUS_CICD,
    PROD_BONUS_MAX,
)
from app.core.logging import get_logger
from app.schemas.analysis import (
    ScoringResult,
    MatchedSkill,
    MissingSkill,
    ProjectExperience,
    CandidateLevel,
    ConfidenceResult,
)

logger = get_logger(__name__)

ACTION_VERBS = {
    "built", "designed", "implemented", "optimized", "deployed", "integrated",
    "architected", "developed", "automated", "created", "engineered", "managed",
    "led", "pioneered", "orchestrated", "scaled", "delivered",
    "fine-tuned", "trained", "evaluated", "monitored", "containerized",
    "indexed", "retrieved",
}

WEAK_EVIDENCE_MARKERS = {"demonstrated capability in", "found directly in resume", "listed skill", "mentioned only"}
SCALE_PATTERN = re.compile(r"\b\d{3,}\b")  # numbers >= 100 indicate scale


def _evidence_level(evidence: str, match_type: str) -> float:
    """
    Determine evidence quality level.

    Returns multiplier 0.40 (MENTIONED) / 0.75 (USED) / 1.00 (BUILT/OWNED).
    """
    ev = evidence.lower().strip()

    # LEVEL 3: BUILT / OWNED — action verb present
    for verb in ACTION_VERBS:
        if verb in ev:
            return EVIDENCE_BUILT_DEPLOYED_SCORE

    # LEVEL 2: USED — project context with reasonable detail
    if len(ev) > 40 and not any(m in ev for m in WEAK_EVIDENCE_MARKERS):
        return EVIDENCE_USED_SCORE

    # LEVEL 1: MENTIONED — generic or very short
    return EVIDENCE_MENTIONED_SCORE


def _has_scale_numbers(evidence: str) -> bool:
    """Check if evidence mentions scale (100+ documents, users, etc.)."""
    return bool(SCALE_PATTERN.search(evidence))


def calculate_score(
    matched_skills: List[MatchedSkill],
    critical_gaps: List[MissingSkill],
    recommended_improvements: List[MissingSkill],
    optional_skills: List[MissingSkill],
    project_experience: List[ProjectExperience],
    semantic_similarity: float,
    candidate_level: Optional[CandidateLevel] = None,
    confidence: Optional[ConfidenceResult] = None,
) -> ScoringResult:
    """
    Calculate a weighted, evidence-aware match score.

    Weights (final):
      - Technical Skill Match:    40%
      - AI Engineering Depth:     25%
      - Semantic Similarity:      20%
      - Production Engineering:   15%
    """

    # ── 1. Technical Skill Match (40%) ──
    matched_weight_sum = 0.0
    evidence_quality_sum = 0.0
    total_weight_sum = 0.0

    for item in matched_skills:
        skill_lower = (item.required_skill or item.skill).lower()

        # Determine importance
        importance = IMPORTANCE_IMPORTANT
        if any(kw in skill_lower for kw in ["python", "fastapi", "flask", "llm", "rag", "embedding", "vector", "rest", "backend", "deep learning", "pytorch", "tensorflow"]):
            importance = IMPORTANCE_CRITICAL
        elif any(kw in skill_lower for kw in ["claude", "openai", "azure", "aws", "gcp", "mlops", "research"]):
            importance = IMPORTANCE_OPTIONAL

        base_weight = IMPORTANCE_WEIGHTS.get(importance, 5.0)
        match_type_w = MATCH_TYPE_WEIGHTS.get(item.match_type, 0.50)
        evidence_w = _evidence_level(item.evidence, item.match_type)
        confidence_w = max(0.25, min(1.0, getattr(item, 'confidence', 1.0)))

        effective_weight = base_weight * match_type_w * evidence_w * confidence_w
        matched_weight_sum += effective_weight
        evidence_quality_sum += evidence_w
        total_weight_sum += base_weight

    # Gaps add to denominator (penalty)
    for critical_item in critical_gaps:
        total_weight_sum += IMPORTANCE_WEIGHTS.get(critical_item.importance, 10.0)
    for rec_item in recommended_improvements:
        total_weight_sum += IMPORTANCE_WEIGHTS.get(rec_item.importance, 5.0)
    for opt_item in optional_skills:
        total_weight_sum += IMPORTANCE_WEIGHTS.get(opt_item.importance, 0.0)  # optional gaps do not penalize

    core_tech_score = (matched_weight_sum / total_weight_sum * 100.0) if total_weight_sum > 0 else 100.0

    # ── 2. AI Engineering Depth / Project Experience (25%) ──
    WEAK_VERBS = ["learn", "explore", "interest", "study", "academic", "tutorial", "course", "class", "student"]
    STRONG_VERBS = ["built", "develop", "design", "implement", "deploy", "optimize", "integrate", "architect", "scale", "create"]

    project_scores = []
    for exp in project_experience:
        if not exp.detected:
            project_scores.append(0.0)
            continue

        ev = exp.evidence.lower()
        has_weak = any(w in ev for w in WEAK_VERBS)
        has_strong = any(s in ev for s in STRONG_VERBS)
        has_scale = _has_scale_numbers(exp.evidence)

        if has_strong and has_scale:
            project_scores.append(PROJECT_SCORE_BUILT_AT_SCALE)
        elif has_strong:
            project_scores.append(PROJECT_SCORE_BUILT)
        elif has_weak and has_strong:
            project_scores.append(PROJECT_SCORE_MIXED)
        elif has_weak:
            project_scores.append(PROJECT_SCORE_LEARNING)
        elif len(exp.evidence) > 30:
            project_scores.append(PROJECT_SCORE_CONTEXT)
        else:
            project_scores.append(PROJECT_SCORE_MINIMAL)

    if project_scores:
        project_exp_score = min(100.0, sum(project_scores) / PROJECT_SCORE_NORMALIZATION_DIVISOR)
    else:
        project_exp_score = 0.0

    # ── 3. Semantic Similarity / Content Match (20%) ──
    semantic_score = max(0.0, min(100.0, semantic_similarity * 100.0))

    # ── 4. Production Engineering Score (15%) ──
    prod_score = 0.0
    prod_bonus_count = 0

    for item in matched_skills:
        skill_lower = (item.required_skill or item.skill).lower()
        evidence_lower = item.evidence.lower()

        # Docker/containerization bonus
        if any(kw in skill_lower for kw in ["docker", "kubernetes", "container"]):
            prod_bonus_count += PROD_BONUS_DOCKER
        if any(kw in evidence_lower for kw in ["docker", "deploy"]):
            prod_bonus_count += PROD_BONUS_DOCKER_EVIDENCE

        # API/backend bonus
        if any(kw in skill_lower for kw in ["fastapi", "flask", "django", "rest"]):
            prod_bonus_count += PROD_BONUS_API

        # Database bonus
        if any(kw in skill_lower for kw in ["postgresql", "mysql", "mongodb", "redis", "database"]):
            prod_bonus_count += PROD_BONUS_DATABASE

        # Testing bonus
        if any(kw in skill_lower for kw in ["pytest", "testing", "unittest", "tdd"]):
            prod_bonus_count += PROD_BONUS_TESTING

        # Cloud bonus
        if any(kw in skill_lower for kw in ["aws", "gcp", "azure", "cloud"]):
            prod_bonus_count += PROD_BONUS_CLOUD

        # CI/CD bonus
        if any(kw in skill_lower for kw in ["ci/cd", "github actions", "jenkins"]):
            prod_bonus_count += PROD_BONUS_CICD

    prod_score = min(PROD_BONUS_MAX, float(prod_bonus_count))

    # ── 5. Final Composite Score ──

    final_float = (
        WEIGHT_TECH_SKILL * core_tech_score
        + WEIGHT_PROJECT_EXP * project_exp_score
        + WEIGHT_SEMANTIC * semantic_score
        + WEIGHT_PRODUCTION * prod_score
    )

    final_score = max(0, min(100, round(final_float)))

    missing_skills = critical_gaps + recommended_improvements + optional_skills

    logger.info(
        "Weighted score calculated",
        extra={
            "core_tech_score": round(core_tech_score, 1),
            "project_exp_score": round(project_exp_score, 1),
            "semantic_score": round(semantic_score, 1),
            "prod_score": round(prod_score, 1),
            "final_score": final_score,
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills),
        },
    )

    return ScoringResult(
        skill_overlap_score=round(core_tech_score, 2),
        semantic_similarity_score=round(semantic_score, 2),
        project_experience_score=round(project_exp_score, 2),
        bonus_score=round(prod_score, 2),
        final_score=final_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        critical_gaps=critical_gaps,
        recommended_improvements=recommended_improvements,
        optional_skills=optional_skills,
        project_experience=project_experience,
        candidate_level=candidate_level,
        confidence=confidence,
    )
