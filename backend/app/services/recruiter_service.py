"""
Recruiter Decision Service.

Generates the final AI recruiter decision based on the computed match score,
skill evidence quality, and gap analysis.

Decision matrix:
  >= 85  -> Strong Interview Candidate   (Risk: Low)
  70-84  -> Potential Candidate           (Risk: Medium)
  < 70   -> Needs Development             (Risk: High)

Does NOT call Gemini. Pure deterministic logic operating on
the already-computed scoring and validation results.
"""
from typing import List, Optional

from app.core.constants import (
    RECRUITER_STRONG_CANDIDATE,
    RECRUITER_POTENTIAL_CANDIDATE,
    RECRUITER_NEEDS_DEVELOPMENT,
    RECRUITER_RISK_LOW,
    RECRUITER_RISK_MEDIUM,
    RECRUITER_RISK_HIGH,
    IMPORTANCE_CRITICAL,
    EXPERIENCE_PRODUCTION,
    EXPERIENCE_PROJECT,
)
from app.core.logging import get_logger
from app.schemas.analysis import (
    MatchedSkill,
    MissingSkill,
    CandidateLevel,
    RecruiterDecision,
    ConfidenceAnalysis,
)

logger = get_logger(__name__)


def _build_reasons(
    decision: str,
    matched_skills: List[MatchedSkill],
    critical_gaps: List[MissingSkill],
    recommended_improvements: List[MissingSkill],
    confidence_analysis: Optional[ConfidenceAnalysis],
    candidate_level: Optional[CandidateLevel],
    final_score: int,
) -> List[str]:
    """Build 3 recruiter-style bullet-point reasons for the decision."""
    reasons: List[str] = []

    # Skill evidence quality
    production_skills = [
        s for s in matched_skills
        if getattr(s, "experience_level", None) == EXPERIENCE_PRODUCTION
    ]
    project_skills = [
        s for s in matched_skills
        if getattr(s, "experience_level", None) == EXPERIENCE_PROJECT
    ]
    critical_matched = [
        s for s in matched_skills
        if (s.importance or "").upper() == IMPORTANCE_CRITICAL
    ]

    if len(production_skills) >= 3:
        skill_names = ", ".join(
            (s.required_skill or s.skill)[:20] for s in production_skills[:3]
        )
        reasons.append(f"Demonstrated production-level experience in: {skill_names}")
    elif len(critical_matched) >= 2:
        skill_names = ", ".join(
            (s.required_skill or s.skill)[:20] for s in critical_matched[:3]
        )
        reasons.append(f"Matched {len(critical_matched)} critical JD requirements including: {skill_names}")
    elif len(project_skills) >= 2:
        reasons.append(f"Project-level experience found across {len(project_skills)} relevant skills")
    elif len(matched_skills) > 0:
        reasons.append(f"Matched {len(matched_skills)} skills from the job description")
    else:
        reasons.append("Limited skill overlap detected with the job description")

    # Gap analysis
    if not critical_gaps:
        reasons.append("No critical skill gaps identified — strong alignment with core requirements")
    elif len(critical_gaps) == 1:
        reasons.append(f"One critical gap: {critical_gaps[0].skill} — manageable with focused learning")
    elif len(critical_gaps) <= 3:
        gap_names = ", ".join(g.skill for g in critical_gaps[:3])
        reasons.append(f"Critical gaps in: {gap_names} — requires targeted development")
    else:
        reasons.append(f"{len(critical_gaps)} critical skill gaps present — significant learning curve expected")

    # Candidate level or score context
    if candidate_level:
        reasons.append(f"Assessed seniority: {candidate_level.candidate_level} — {candidate_level.reason[:80]}")
    elif confidence_analysis and confidence_analysis.reasons:
        reasons.append(confidence_analysis.reasons[0])
    else:
        if final_score >= 85:
            reasons.append("Overall profile demonstrates strong readiness for the role")
        elif final_score >= 70:
            reasons.append("Profile shows promise with some areas requiring development")
        else:
            reasons.append("Profile requires significant skill development before role readiness")

    return reasons[:3]  # Return exactly 3 reasons


def make_decision(
    final_score: int,
    matched_skills: List[MatchedSkill],
    critical_gaps: List[MissingSkill],
    recommended_improvements: List[MissingSkill],
    candidate_level: Optional[CandidateLevel],
    confidence_analysis: Optional[ConfidenceAnalysis],
) -> RecruiterDecision:
    """
    Generate the final recruiter hiring decision.

    Args:
        final_score: Overall match score (0-100).
        matched_skills: Validated matched skills (with experience_level).
        critical_gaps: CRITICAL missing skills.
        recommended_improvements: IMPORTANT missing skills.
        candidate_level: Seniority assessment from Gemini extraction.
        confidence_analysis: Analysis confidence from confidence_service.

    Returns:
        RecruiterDecision with decision, risk_level, and reasons.
    """
    # Primary decision based on final score
    critical_gap_count = len(critical_gaps)

    if final_score >= 85 and critical_gap_count <= 2:
        decision = RECRUITER_STRONG_CANDIDATE
        risk_level = RECRUITER_RISK_LOW
    elif final_score >= 85 and critical_gap_count > 2:
        # High score but many critical gaps
        decision = RECRUITER_POTENTIAL_CANDIDATE
        risk_level = RECRUITER_RISK_MEDIUM
    elif final_score >= 70:
        decision = RECRUITER_POTENTIAL_CANDIDATE
        risk_level = RECRUITER_RISK_MEDIUM if critical_gap_count <= 2 else RECRUITER_RISK_HIGH
    else:
        decision = RECRUITER_NEEDS_DEVELOPMENT
        risk_level = RECRUITER_RISK_HIGH

    # Upgrade/downgrade based on evidence quality
    production_count = sum(
        1 for s in matched_skills
        if getattr(s, "experience_level", None) == EXPERIENCE_PRODUCTION
    )

    # Downgrade: No production evidence for a senior role requirement
    if production_count == 0 and final_score >= 85:
        if decision == RECRUITER_STRONG_CANDIDATE:
            risk_level = RECRUITER_RISK_MEDIUM  # Keep decision but increase risk

    # Upgrade: Excellent evidence despite borderline score
    if production_count >= 5 and final_score >= 75 and decision == RECRUITER_POTENTIAL_CANDIDATE:
        risk_level = RECRUITER_RISK_LOW  # Keep Potential but lower risk

    candidate_level_str = ""
    if candidate_level:
        candidate_level_str = candidate_level.candidate_level

    reasons = _build_reasons(
        decision=decision,
        matched_skills=matched_skills,
        critical_gaps=critical_gaps,
        recommended_improvements=recommended_improvements,
        confidence_analysis=confidence_analysis,
        candidate_level=candidate_level,
        final_score=final_score,
    )

    logger.info(
        "Recruiter decision made",
        extra={
            "decision": decision,
            "risk_level": risk_level,
            "final_score": final_score,
            "critical_gaps": critical_gap_count,
        },
    )

    return RecruiterDecision(
        decision=decision,
        risk_level=risk_level,
        reasons=reasons,
        candidate_level=candidate_level_str,
    )
