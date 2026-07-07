"""
Evidence Validator Service.

Validates every extracted matched skill against actual resume evidence,
classifying each skill into one of three experience levels:

  - Mention Only       (skill listed but no project context found)  -> confidence 50
  - Project Experience (skill used in a project context)            -> confidence 80
  - Production Experience (deployed/scaled/owned production system) -> confidence 95

Does NOT make any Gemini calls. Uses regex section parsing + action verb heuristics
+ the existing cross-encoder reranker for borderline cases.
"""
import re
from typing import List, Tuple

from app.core.constants import (
    EXPERIENCE_MENTION_ONLY,
    EXPERIENCE_PROJECT,
    EXPERIENCE_PRODUCTION,
    EXPERIENCE_CONFIDENCE,
    EVIDENCE_CROSS_ENCODER_THRESHOLD,
)
from app.core.logging import get_logger
from app.schemas.analysis import MatchedSkill, SkillEvidence
from app.services.reranker_service import validate_match

logger = get_logger(__name__)

# Section header patterns for structured resume parsing
_SECTION_PATTERNS = {
    "experience": re.compile(
        r"(?i)^(work\s+)?experience|employment|professional\s+background|career\s+history",
        re.MULTILINE,
    ),
    "projects": re.compile(
        r"(?i)^projects?|personal\s+projects?|academic\s+projects?|side\s+projects?",
        re.MULTILINE,
    ),
    "skills": re.compile(
        r"(?i)^(technical\s+)?skills?|technologies|competencies|tools",
        re.MULTILINE,
    ),
    "summary": re.compile(
        r"(?i)^(professional\s+)?summary|objective|profile|about\s+(me|myself)",
        re.MULTILINE,
    ),
}

# Action verbs that indicate Production Experience
_PRODUCTION_VERBS = {
    "deployed", "launched", "released", "shipped", "containerized",
    "scaled", "architected", "led", "owned", "orchestrated", "maintained",
    "monitored", "automated", "optimized", "delivered", "migrated",
}

# Action verbs indicating Project Experience
_PROJECT_VERBS = {
    "built", "developed", "implemented", "created", "designed",
    "integrated", "engineered", "constructed", "wrote", "produced",
    "configured", "set up", "established", "trained", "fine-tuned",
    "indexed", "retrieved", "embedded",
}

# Markers of weakness / mention-only evidence
_WEAK_MARKERS = {
    "familiar with", "knowledge of", "exposure to", "interest in",
    "learning", "studying", "course", "tutorial", "academic",
    "basic understanding", "beginner",
}


def _parse_sections(resume_text: str) -> dict:
    """
    Splits resume into named sections.
    Returns a dict mapping section name to raw text.
    """
    lines = resume_text.split("\n")
    sections = {"skills": [], "experience": [], "projects": [], "summary": [], "other": []}
    current_section = "other"

    for line in lines:
        stripped = line.strip()
        matched_section = None
        for sec_name, pattern in _SECTION_PATTERNS.items():
            if pattern.match(stripped):
                matched_section = sec_name
                break
        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}


def _classify_experience(skill_name: str, evidence_text: str, section: str) -> Tuple[str, int]:
    """
    Classify experience level based on evidence text and section context.

    Returns (experience_level, confidence_score).
    """
    ev_lower = evidence_text.lower()

    # Check for weak markers first — overrides everything
    if any(marker in ev_lower for marker in _WEAK_MARKERS):
        return EXPERIENCE_MENTION_ONLY, EXPERIENCE_CONFIDENCE[EXPERIENCE_MENTION_ONLY]

    # Skills section with no project context -> Mention Only
    if section == "skills" and len(evidence_text.strip()) < 40:
        return EXPERIENCE_MENTION_ONLY, EXPERIENCE_CONFIDENCE[EXPERIENCE_MENTION_ONLY]

    # Production verbs in evidence -> Production Experience
    ev_words = set(re.findall(r'\b\w+\b', ev_lower))
    if _PRODUCTION_VERBS & ev_words:
        return EXPERIENCE_PRODUCTION, EXPERIENCE_CONFIDENCE[EXPERIENCE_PRODUCTION]

    # Project verbs in evidence -> Project Experience
    if _PROJECT_VERBS & ev_words:
        return EXPERIENCE_PROJECT, EXPERIENCE_CONFIDENCE[EXPERIENCE_PROJECT]

    # Evidence has substantial length and is not in the skills section
    if section in ("experience", "projects") and len(evidence_text.strip()) > 50:
        return EXPERIENCE_PROJECT, EXPERIENCE_CONFIDENCE[EXPERIENCE_PROJECT]

    # Fallback: Mention Only
    return EXPERIENCE_MENTION_ONLY, EXPERIENCE_CONFIDENCE[EXPERIENCE_MENTION_ONLY]


def _find_best_evidence(skill_name: str, sections: dict) -> Tuple[str, str, float]:
    """
    Search all resume sections for the best evidence sentence for a skill.

    Returns (evidence_text, section_name, best_score).
    Prioritises: experience -> projects -> summary -> skills -> other.
    """
    skill_lower = skill_name.lower()
    skill_words = [w for w in skill_lower.split() if len(w) > 2]
    priority = ["experience", "projects", "summary", "skills", "other"]

    best_sentence = ""
    best_section = "skills"
    best_score = 0.0

    for sec_name in priority:
        section_text = sections.get(sec_name, "")
        if not section_text.strip():
            continue

        sentences = [s.strip() for s in re.split(r"[.!\n]", section_text) if len(s.strip()) > 10]
        for sentence in sentences:
            sent_lower = sentence.lower()
            # Quick keyword check to limit cross-encoder calls
            if not (skill_lower in sent_lower or any(w in sent_lower for w in skill_words)):
                continue

            try:
                score = validate_match(skill_name, sentence)
            except Exception:
                # Fallback to simple substring match if cross-encoder fails
                score = 0.8 if skill_lower in sent_lower else 0.3

            if score > best_score:
                best_score = score
                best_sentence = sentence
                best_section = sec_name

            # Good enough — stop searching
            if best_score >= EVIDENCE_CROSS_ENCODER_THRESHOLD:
                break

        if best_score >= EVIDENCE_CROSS_ENCODER_THRESHOLD:
            break

    return best_sentence, best_section, best_score


def validate_skills(
    matched_skills: List[MatchedSkill],
    resume_text: str,
) -> Tuple[List[MatchedSkill], List[SkillEvidence]]:
    """
    Validate every matched skill against resume evidence.

    Returns:
      - enriched_skills: matched_skills list with experience_level populated
      - unverified: skills where confidence is low (evidence not found or weak)
    """
    sections = _parse_sections(resume_text)
    enriched: List[MatchedSkill] = []
    unverified: List[SkillEvidence] = []

    for skill in matched_skills:
        skill_name = skill.required_skill or skill.skill

        # If Gemini already provided good evidence, use it directly
        existing_evidence = (skill.evidence or "").strip()

        if existing_evidence and len(existing_evidence) > 25:
            # Classify based on existing Gemini evidence
            exp_level, conf = _classify_experience(skill_name, existing_evidence, "experience")
            evidence_text = existing_evidence
            evidence_section = "resume"
        else:
            # No good evidence from Gemini — search resume sections
            evidence_text, evidence_section, cross_score = _find_best_evidence(skill_name, sections)
            if cross_score >= EVIDENCE_CROSS_ENCODER_THRESHOLD:
                exp_level, conf = _classify_experience(skill_name, evidence_text, evidence_section)
            elif cross_score > 0.3:
                exp_level = EXPERIENCE_MENTION_ONLY
                conf = EXPERIENCE_CONFIDENCE[EXPERIENCE_MENTION_ONLY]
            else:
                # No evidence found at all
                exp_level = EXPERIENCE_MENTION_ONLY
                conf = 30

        # Enrich the skill
        skill.experience_level = exp_level
        enriched.append(skill)

        # Mark as unverified if confidence is below threshold
        if conf < 60:
            unverified.append(SkillEvidence(
                skill_name=skill_name,
                is_verified=False,
                confidence_score=conf,
                evidence_text=evidence_text or "No direct evidence found",
                evidence_section=evidence_section,
                experience_level=exp_level,
            ))
            logger.debug(f"EvidenceValidator: Low confidence for '{skill_name}' ({conf}%): {exp_level}")
        else:
            logger.debug(f"EvidenceValidator: Verified '{skill_name}' at '{exp_level}' ({conf}%)")

    logger.info(
        "Evidence validation complete",
        extra={
            "total_skills": len(matched_skills),
            "unverified_count": len(unverified),
        },
    )
    return enriched, unverified
