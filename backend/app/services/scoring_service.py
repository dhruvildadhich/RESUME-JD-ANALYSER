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
    EXACT_MATCH,
    EXACT,
    EQUIVALENT_MATCH,
    EQUIVALENT,
    PARTIAL_MATCH,
    PARTIAL,
    EVIDENCE_MENTIONED_SCORE,
    EVIDENCE_USED_SCORE,
    EVIDENCE_BUILT_DEPLOYED_SCORE,
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
    ScoreBreakdown,
    SkillEvidence,
    ConfidenceAnalysis,
    RecruiterDecision,
    ImprovementSuggestion,
    MatchedSkill,
    MissingSkill,
    ProjectExperience,
    CandidateLevel,
    ConfidenceResult,
)
from app.config.settings import get_settings

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
    semantic_similarity: dict,
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
    critical_earned = 0.0
    important_earned = 0.0
    optional_earned = 0.0

    critical_matched_count = 0
    important_matched_count = 0
    optional_matched_count = 0

    for item in matched_skills:
        # Assign points based on match type
        if item.match_type in (EXACT_MATCH, EXACT):
            match_val = 1.0
        elif item.match_type in (EQUIVALENT_MATCH, EQUIVALENT):
            match_val = 0.9
        elif item.match_type in (PARTIAL_MATCH, PARTIAL):
            match_val = 0.7
        else:
            match_val = 0.5
            
        imp = item.importance.upper() if getattr(item, 'importance', None) else "IMPORTANT"
        if imp == "CRITICAL":
            critical_earned += match_val
            critical_matched_count += 1
        elif imp == "OPTIONAL":
            optional_earned += match_val
            optional_matched_count += 1
        else:
            important_earned += match_val
            important_matched_count += 1

    total_critical = critical_matched_count + len(critical_gaps)
    total_important = important_matched_count + len(recommended_improvements)
    total_optional = optional_matched_count + len(optional_skills)

    earned_weight = 0.0
    total_weight = 0.0

    if total_critical > 0:
        critical_score = critical_earned / total_critical
        earned_weight += critical_score * 0.50
        total_weight += 0.50
    else:
        critical_score = 0.0

    if total_important > 0:
        important_score = important_earned / total_important
        earned_weight += important_score * 0.30
        total_weight += 0.30
    else:
        important_score = 0.0

    if total_optional > 0:
        optional_score = optional_earned / total_optional
        earned_weight += optional_score * 0.20
        total_weight += 0.20
    else:
        optional_score = 0.0

    core_tech_score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 100.0

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

        base_score = 0.0
        if has_strong and has_scale:
            base_score = PROJECT_SCORE_BUILT_AT_SCALE
        elif has_strong:
            base_score = PROJECT_SCORE_BUILT
        elif has_weak and has_strong:
            base_score = PROJECT_SCORE_MIXED
        elif has_weak:
            base_score = PROJECT_SCORE_LEARNING
        elif len(exp.evidence) > 30:
            base_score = PROJECT_SCORE_CONTEXT
        else:
            base_score = PROJECT_SCORE_MINIMAL

        # Apply AI topic multipliers
        exp_topic = exp.experience.lower()
        if any(kw in exp_topic for kw in ["rag", "agent", "vector", "fine-tuning", "ml pipeline", "model deployment", "model training"]):
            base_score *= 1.5
        elif any(kw in exp_topic for kw in ["crud", "api", "rest", "backend", "web"]):
            base_score *= 0.8

        project_scores.append(base_score)

    if project_scores:
        project_exp_score = min(100.0, sum(project_scores) / PROJECT_SCORE_NORMALIZATION_DIVISOR)
    else:
        project_exp_score = 0.0

    # ── 3. Semantic Similarity / Content Match (20%) ──
    # Support dict from new hybrid embedding service, fallback to float if old format
    if isinstance(semantic_similarity, dict):
        final_sim = semantic_similarity.get("final_semantic_score", 0.0)
        skill_sim = semantic_similarity.get("skill_semantic_score", 0.0)
        proj_sim = semantic_similarity.get("project_semantic_score", 0.0)
        exp_sim = semantic_similarity.get("experience_semantic_score", 0.0)
    else:
        final_sim = float(semantic_similarity)
        skill_sim = proj_sim = exp_sim = final_sim

    # Normalize BGE cosine similarity into ATS interpretation
    if final_sim >= 0.75:
        # Excellent semantic match
        semantic_score = 90.0 + (min(1.0, final_sim) - 0.75) * (10.0 / 0.25)
    elif final_sim >= 0.65:
        # Strong semantic match
        semantic_score = 80.0 + (final_sim - 0.65) * (9.0 / 0.10)
    elif final_sim >= 0.50:
        # Moderate match
        semantic_score = 65.0 + (final_sim - 0.50) * (14.0 / 0.15)
    else:
        # Weak match
        semantic_score = max(0.0, final_sim * (64.0 / 0.50))

    # ── 4. Production Engineering Score (15%) ──
    # Evaluate a balanced set of production dimensions instead of just counting instances
    prod_dimensions_found = set()

    for item in matched_skills:
        skill_lower = (item.required_skill or item.skill).lower()
        evidence_lower = item.evidence.lower()
        combined_text = skill_lower + " " + evidence_lower

        if any(kw in combined_text for kw in ["docker", "kubernetes", "container"]):
            prod_dimensions_found.add("containerization")
        if any(kw in combined_text for kw in ["aws", "gcp", "azure", "cloud"]):
            prod_dimensions_found.add("cloud")
        if any(kw in combined_text for kw in ["ci/cd", "github actions", "jenkins", "gitlab ci", "pipeline"]):
            prod_dimensions_found.add("cicd")
        if any(kw in combined_text for kw in ["pytest", "testing", "unittest", "tdd", "integration test"]):
            prod_dimensions_found.add("testing")
        if any(kw in combined_text for kw in ["monitor", "grafana", "prometheus", "datadog", "observability"]):
            prod_dimensions_found.add("monitoring")
        if any(kw in combined_text for kw in ["log", "elk", "splunk", "kibana"]):
            prod_dimensions_found.add("logging")
        if any(kw in combined_text for kw in ["deploy", "production", "scale", "infrastructure"]):
            prod_dimensions_found.add("deployment")
            
    # Base calculation: Each distinct production dimension is worth ~15 points out of 100 max
    prod_score = min(100.0, len(prod_dimensions_found) * 15.0)

    # ── 5. Final Composite Score ──
    settings = get_settings()
    final_float = (
        core_tech_score * settings.skill_weight
        + semantic_score * settings.semantic_weight
    )

    final_score = max(0, min(100, round(final_float)))
    
    # ── 6. Sanity Validation Layer ──
    # If the candidate has many matched skills and few critical gaps, ensure their score reflects ATS expectations.
    if len(matched_skills) > 30 and len(critical_gaps) <= 2 and semantic_score >= 80.0:
        final_score = max(80, final_score)

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
        skill_overlap_score=core_tech_score,
        semantic_similarity_score=semantic_score,
        skill_semantic_score=max(0.0, min(100.0, skill_sim * 100.0)),
        project_semantic_score=max(0.0, min(100.0, proj_sim * 100.0)),
        experience_semantic_score=max(0.0, min(100.0, exp_sim * 100.0)),
        project_experience_score=project_exp_score,
        bonus_score=prod_score,
        final_score=final_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        critical_gaps=critical_gaps,
        recommended_improvements=recommended_improvements,
        optional_skills=optional_skills,
        project_experience=project_experience,
        candidate_level=candidate_level,
        confidence=confidence,
        score_breakdown=ScoreBreakdown(
            critical_match=critical_score * 100.0,
            important_match=important_score * 100.0,
            optional_match=optional_score * 100.0,
            semantic_score=semantic_score
        ),
    )
