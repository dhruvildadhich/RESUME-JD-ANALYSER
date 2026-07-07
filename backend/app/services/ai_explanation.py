"""
AI Explanation Service.

Uses Gemini to generate a rich, structured analysis of the candidate's
resume against the job description. Returns matched skills, missing skills,
strengths, weaknesses, improvement suggestions, and a hiring recommendation.
"""
import json
import re
from typing import Any

from google import genai

from app.config.settings import get_settings
from app.core.constants import (
    RECOMMENDATION_STRONG_MATCH,
    RECOMMENDATION_GOOD_POTENTIAL,
    RECOMMENDATION_NEEDS_IMPROVEMENT,
    RECOMMENDATION_NOT_RECOMMENDED,
)
from app.core.logging import get_logger
from app.schemas.analysis import MatchedSkill, MissingSkill, SkillExtractionResult
from app.core.cache import get_cached_explanation, set_cached_explanation
from google.genai.errors import ClientError, ServerError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import httpx
import requests

logger = get_logger(__name__)

_EXPLANATION_PROMPT = """
You are a senior technical recruiter and AI systems architect with 15+ years of experience.
Evaluate the candidate's resume against the job description and the computed match metrics.

Computed Match Metrics:
- Match Score: {match_score}%
- Matched Skills & Categories: {matched_skills}
- Missing Skills & Importance: {missing_skills}

RESUME TEXT:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Analyze the experience depth, equivalent tooling (e.g. Weaviate/Pinecone category overlap), project details, and overall suitability.

Return ONLY a valid JSON object with this exact structure:
{{
  "strengths": [
    "Strength 1: Highlighting a key technical alignment with evidence.",
    "Strength 2: Detail regarding complex project implementation.",
    "Strength 3: Practical experience alignment."
  ],
  "weaknesses": [
    "Critical Gaps: List critical skills missing and how they impact fit.",
    "Optional Gaps: List optional missing skills and explain why they have low impact due to equivalent tool usage."
  ],
  "explanation": "A professional 3-4 sentence narrative summarizing the candidate's overall fit, equivalent skills, and core engineering strengths.",
  "suggestions": [
    "Actionable tip 1: Detail a concrete project or tool to learn to cover critical gaps.",
    "Actionable tip 2: Suggested certifications or architecture designs.",
    "Actionable tip 3: Advanced MLOps/cloud capabilities to add."
  ],
  "hiring_recommendation": "Strong Match | Good Potential Match | Needs Improvement | Not Recommended"
}}

Hiring Recommendation Guidelines:
- "Strong Match": Satisfies all/most critical requirements, strong AI project evidence (80+ score).
- "Good Potential Match": Strong core practical experience (FastAPI, RAG, Python) but missing some advanced/optional items (60-79 score).
- "Needs Improvement": Has foundation but missing crucial critical skills (40-59 score).
- "Not Recommended": Major critical areas completely missing (below 40 score).

Return ONLY the JSON. No markdown, no code fences, no extra text.
"""


def generate_explanation(
    resume_text: str,
    jd_text: str,
    match_score: int,
    matched_skills: list[MatchedSkill],
    critical_gaps: list[MissingSkill],
    recommended_improvements: list[MissingSkill],
    optional_skills: list[MissingSkill],
    extraction_result: SkillExtractionResult | None = None,
) -> dict[str, Any]:
    """
    Generate a structured AI explanation using Gemini.
    """
    # If extraction phase failed and fell back, immediately use the local generator
    if extraction_result and extraction_result.fallback_mode:
        logger.info(
            "Extraction fell back to local mode. Skipping Gemini explanation call and using local generator.",
            extra={"fallback_mode": True}
        )
        return generate_explanation_fallback(
            matched_skills,
            critical_gaps,
            recommended_improvements,
            optional_skills,
            match_score
        )

    # Reuse explanation data from extraction phase to avoid a second Gemini call
    if extraction_result and extraction_result.explanation:
        logger.info(
            "Explanation reused from Gemini extraction result, skipping explanation call",
            extra={"gemini_explanation_reused": True},
        )
        return {
            "strengths": extraction_result.strengths,
            "weaknesses": extraction_result.weaknesses,
            "explanation": extraction_result.explanation,
            "suggestions": extraction_result.suggestions,
            "hiring_recommendation": extraction_result.hiring_recommendation,
        }

    # Serialization for caching
    score_data = {
        "match_score": match_score,
        "matched_skills": [m.model_dump() for m in matched_skills],
        "critical_gaps": [m.model_dump() for m in critical_gaps],
        "recommended_improvements": [m.model_dump() for m in recommended_improvements],
        "optional_skills": [m.model_dump() for m in optional_skills],
    }
    score_result_json = json.dumps(score_data, sort_keys=True)
    extraction_result_json = extraction_result.model_dump_json() if extraction_result else ""
    cached_explanation = get_cached_explanation(score_result_json, extraction_result_json)
    if cached_explanation is not None:
        logger.info("Using cached Gemini AI explanation")
        return cached_explanation

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)

    missing_skills = critical_gaps + recommended_improvements + optional_skills

    # Format the structured lists into readable context string for Gemini prompt
    matched_str = ", ".join([f"{item.skill} ({item.category})" for item in matched_skills]) if matched_skills else "None"
    missing_str = ", ".join([f"{item.skill} ({item.importance}: {item.note})" for item in missing_skills]) if missing_skills else "None"

    prompt = _EXPLANATION_PROMPT.format(
        match_score=match_score,
        matched_skills=matched_str,
        missing_skills=missing_str,
        resume_text=resume_text[:5000],
        jd_text=jd_text[:2500],
    )

    try:
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
        def _call_gemini_with_retry():
            logger.info(f"Calling Gemini API ({settings.gemini_explanation_model}) for AI explanation")
            return client.models.generate_content(
                model=settings.gemini_explanation_model,
                contents=prompt,
            )

        response = _call_gemini_with_retry()
        raw_text = response.text.strip()

        # Strip markdown fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        payload = json.loads(cleaned)

        # Validate required keys
        required_keys = {"strengths", "weaknesses", "explanation", "suggestions", "hiring_recommendation"}
        missing_keys = required_keys - set(payload.keys())
        if missing_keys:
            raise ValueError(f"Missing keys in Gemini response: {missing_keys}")

        # Store to cache
        set_cached_explanation(score_result_json, extraction_result_json, payload)

    except ClientError as exc:
        if exc.code == 429:
            logger.warning("Gemini quota exceeded. Local fallback activated.")
        elif exc.code in (401, 403):
            logger.warning("Gemini authentication failed.")
        else:
            logger.warning(
                f"Gemini ClientError ({exc.code}). Local fallback activated.",
                extra={"error": str(exc)}
            )
        payload = generate_explanation_fallback(matched_skills, critical_gaps, recommended_improvements, optional_skills, match_score)
    except Exception as exc:
        logger.warning(
            "Gemini explanation generation failed. Falling back to local heuristic explanation generator.",
            extra={"error": str(exc)},
            exc_info=True
        )
        payload = generate_explanation_fallback(matched_skills, critical_gaps, recommended_improvements, optional_skills, match_score)

    logger.info(
        "AI explanation generated",
        extra={"recommendation": payload.get("hiring_recommendation", "unknown")},
    )
    return payload


def generate_explanation_fallback(
    matched_skills: list[MatchedSkill],
    critical_gaps: list[MissingSkill],
    recommended_improvements: list[MissingSkill],
    optional_skills: list[MissingSkill],
    match_score: int
) -> dict[str, Any]:
    """Generates a high-quality heuristic explanation when Gemini is unavailable."""
    strengths = []
    weaknesses = []
    suggestions = []
    
    # Strengths based on matching skills
    matched_names = [item.skill for item in matched_skills]
    if matched_skills:
        strengths.append(f"Demonstrates core competency in normalized categories: {', '.join(list(set([item.category for item in matched_skills[:3]])))}.")
        strengths.append(f"Hands-on project evidence found for skills: {', '.join(matched_names[:4])}.")
        strengths.append("Possesses practical experience building and deploying API endpoints or applications.")
    else:
        strengths.append("Candidate has general software development foundations.")

    # Weaknesses grouped into Critical and Optional gaps
    if critical_gaps:
        weaknesses.append(f"Critical Gaps: Lacks explicit experience with critical technologies: {', '.join([item.skill for item in critical_gaps[:3]])}.")
    if recommended_improvements or optional_skills:
        optional_missing = recommended_improvements + optional_skills
        weaknesses.append(f"Optional/Secondary Gaps: Missing preferred tools: {', '.join([item.skill for item in optional_missing[:3]])}. These can be learned on the job.")
    if not critical_gaps and not recommended_improvements and not optional_skills:
        weaknesses.append("No notable skill gaps identified relative to the job requirements.")

    # Actionable suggestions
    if critical_gaps:
        for skill in [item.skill for item in critical_gaps[:2]]:
            suggestions.append(f"Build a standalone backend or pipeline showcasing hands-on usage of {skill}.")
    if recommended_improvements:
        for skill in [item.skill for item in recommended_improvements[:2]]:
            suggestions.append(f"Familiarize yourself with {skill} to broaden toolset options.")
            
    if not suggestions:
        suggestions.append("Incorporate quantitative achievements and architecture scaling details to project descriptions.")

    # Recruiter recommendations matching the new levels
    if match_score >= 80:
        recommendation = RECOMMENDATION_STRONG_MATCH
        explanation = f"The candidate shows exceptional alignment ({match_score}%) with strong project evidence matching all critical categories."
    elif match_score >= 60:
        recommendation = RECOMMENDATION_GOOD_POTENTIAL
        explanation = f"The candidate has strong practical experience ({match_score}%) covering critical technical skills. Missing some optional tools, which are easily acquired on the job."
    elif match_score >= 40:
        recommendation = RECOMMENDATION_NEEDS_IMPROVEMENT
        explanation = f"The candidate matches some foundations ({match_score}%) but is missing several critical core competencies required for immediate success."
    else:
        recommendation = RECOMMENDATION_NOT_RECOMMENDED
        explanation = f"The candidate alignment is low ({match_score}%) with major required skill categories missing from the resume."

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "explanation": explanation,
        "suggestions": suggestions,
        "hiring_recommendation": recommendation
    }

