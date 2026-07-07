"""
Confidence Service.

Computes a rich, evidence-based analysis confidence score that tells
the recruiter how much to trust the AI's evaluation.

Formula:
    confidence = (
        verified_skill_ratio * 0.40
        + semantic_confidence  * 0.30
        + resume_evidence_quality * 0.30
    )

Confidence levels:
    90-100  HIGH
    70-89   MEDIUM
    0-69    LOW
"""
from typing import List

from app.core.constants import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    EXPERIENCE_MENTION_ONLY,
    EXPERIENCE_PROJECT,
    EXPERIENCE_PRODUCTION,
)
from app.core.logging import get_logger
from app.schemas.analysis import (
    MatchedSkill,
    SkillEvidence,
    ProjectExperience,
    ConfidenceAnalysis,
)

logger = get_logger(__name__)


def _resume_evidence_quality(
    matched_skills: List[MatchedSkill],
    project_experience: List[ProjectExperience],
) -> float:
    """
    Rate overall resume evidence quality (0-100).

    Considers:
    - Proportion of skills with production/project evidence
    - Whether meaningful project experience was detected
    - Average evidence text length (longer = more specific)
    """
    if not matched_skills:
        return 0.0

    experience_scores = []
    for skill in matched_skills:
        level = getattr(skill, "experience_level", None)
        if level == EXPERIENCE_PRODUCTION:
            experience_scores.append(1.0)
        elif level == EXPERIENCE_PROJECT:
            experience_scores.append(0.75)
        else:
            experience_scores.append(0.35)

    evidence_ratio = sum(experience_scores) / len(experience_scores)

    # Bonus for detected project experience patterns
    detected_count = sum(1 for p in project_experience if p.detected)
    project_bonus = min(0.25, detected_count * 0.05)

    # Average evidence text length bonus (cap at 0.15)
    avg_len = sum(len(s.evidence or "") for s in matched_skills) / len(matched_skills)
    length_bonus = min(0.15, avg_len / 500.0)

    raw = evidence_ratio + project_bonus + length_bonus
    return min(100.0, raw * 100.0)


def _semantic_confidence(semantic_similarity_score: float) -> float:
    """
    Map semantic similarity score (0-100) to confidence contribution (0-100).
    """
    if semantic_similarity_score >= 85.0:
        return 100.0
    elif semantic_similarity_score >= 70.0:
        return 80.0 + (semantic_similarity_score - 70.0) * (20.0 / 15.0)
    elif semantic_similarity_score >= 55.0:
        return 60.0 + (semantic_similarity_score - 55.0) * (20.0 / 15.0)
    else:
        return max(0.0, semantic_similarity_score * (60.0 / 55.0))


def _build_reasons(
    verified_ratio: float,
    sem_conf: float,
    ev_quality: float,
    matched_skills: List[MatchedSkill],
    unverified: List[SkillEvidence],
    project_experience: List[ProjectExperience],
) -> List[str]:
    """Build human-readable reasons for the confidence level."""
    reasons: List[str] = []

    # Evidence quality reasons
    production_count = sum(
        1 for s in matched_skills
        if getattr(s, "experience_level", None) == EXPERIENCE_PRODUCTION
    )
    project_count = sum(
        1 for s in matched_skills
        if getattr(s, "experience_level", None) == EXPERIENCE_PROJECT
    )

    if production_count >= 3:
        reasons.append(f"Strong production evidence found for {production_count} skills")
    elif project_count >= 3:
        reasons.append(f"Project-level evidence found for {project_count} skills")
    elif unverified:
        reasons.append(f"{len(unverified)} skill(s) have weak or no resume evidence")

    # Semantic agreement
    if sem_conf >= 85.0:
        reasons.append("High semantic alignment between resume and JD content")
    elif sem_conf >= 65.0:
        reasons.append("Moderate semantic alignment detected")
    else:
        reasons.append("Low semantic similarity — content depth mismatch detected")

    # Project experience
    detected_projects = [p for p in project_experience if p.detected]
    if detected_projects:
        reasons.append(f"Verified AI/system experience patterns: {', '.join(p.experience[:30] for p in detected_projects[:2])}")
    else:
        reasons.append("No structured AI/system project patterns detected")

    # Verified ratio
    if verified_ratio >= 0.85:
        reasons.append("Most critical skills backed by concrete resume evidence")
    elif verified_ratio >= 0.60:
        reasons.append("Majority of skills have traceable evidence")
    else:
        reasons.append("Several key skills lack verifiable resume context")

    return reasons[:4]  # Keep the top 4 most relevant


def compute_confidence(
    matched_skills: List[MatchedSkill],
    unverified_skills: List[SkillEvidence],
    project_experience: List[ProjectExperience],
    semantic_similarity_score: float,
) -> ConfidenceAnalysis:
    """
    Compute overall analysis confidence.

    Args:
        matched_skills: All matched skills (with experience_level populated).
        unverified_skills: Skills flagged as low-evidence by evidence_validator.
        project_experience: Project experience patterns from Gemini extraction.
        semantic_similarity_score: Final semantic score (0-100) from scoring service.

    Returns:
        ConfidenceAnalysis with score, level, and human-readable reasons.
    """
    total = len(matched_skills)

    # Verified skill ratio
    if total > 0:
        unverified_count = len(unverified_skills)
        verified_ratio = max(0.0, (total - unverified_count) / total)
    else:
        verified_ratio = 0.0

    sem_conf = _semantic_confidence(semantic_similarity_score)
    ev_quality = _resume_evidence_quality(matched_skills, project_experience)

    raw_confidence = (
        verified_ratio * 40.0
        + (sem_conf / 100.0) * 30.0
        + (ev_quality / 100.0) * 30.0
    )
    confidence_score = max(0, min(100, round(raw_confidence)))

    if confidence_score >= CONFIDENCE_HIGH_THRESHOLD:
        level = CONFIDENCE_HIGH
    elif confidence_score >= CONFIDENCE_MEDIUM_THRESHOLD:
        level = CONFIDENCE_MEDIUM
    else:
        level = CONFIDENCE_LOW

    reasons = _build_reasons(
        verified_ratio, sem_conf, ev_quality,
        matched_skills, unverified_skills, project_experience,
    )

    logger.info(
        "Confidence analysis complete",
        extra={
            "confidence_score": confidence_score,
            "level": level,
            "verified_ratio": round(verified_ratio, 2),
        },
    )

    return ConfidenceAnalysis(
        confidence_score=confidence_score,
        level=level,
        reasons=reasons,
    )
