"""
Skill Extraction Service.

Uses the Gemini API to extract and normalise technical skills, determine their importance,
extract project evidence, and detect system architecture depth in a single structured JSON call.
"""
import json
import re
from typing import Any

from google import genai

from app.config.settings import get_settings
from app.core.constants import (
    IMPORTANCE_CRITICAL,
    IMPORTANCE_IMPORTANT,
    CONFIDENCE_MEDIUM,
)
from app.core.logging import get_logger
from app.schemas.analysis import SkillExtractionResult, MatchedSkill, MissingSkill, ProjectExperience, CandidateLevel, ConfidenceResult
from app.services.local_skill_extractor import extract_skills_fallback, post_process_extraction_result
from app.core.cache import get_cached_extraction, set_cached_extraction
from google.genai.errors import ClientError, ServerError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import httpx
import requests
import time

logger = get_logger(__name__)

gemini_generation_disabled_until = 0.0
PROMPT_VERSION = "v1"

GEMINI_EXTRACTION_PROMPT = """
You are a senior technical recruiter and AI systems engineer. Analyse the provided candidate RESUME and JOB DESCRIPTION (JD).

Perform an intelligent skill matching and category normalisation. Do not do simple keyword matching. 
Crucially: Do NOT mark equivalent technologies as the exact same skill.
For example, if a candidate has FastAPI and the JD asks for Flask, you must output an EQUIVALENT_MATCH, listing Flask as the required skill and FastAPI as the candidate skill.

Return ONLY a valid JSON object with this exact structure:
{{
  "matched_skills": [
    {{
      "skill": "Normalized Competency Category (e.g. Python Backend Development)",
      "required_skill": "Technology from JD (e.g. Flask)",
      "candidate_skill": "Technology from Resume (e.g. FastAPI)",
      "match_type": "EXACT_MATCH | EQUIVALENT_MATCH | PARTIAL_MATCH",
      "evidence": "Concrete sentence or implementation details from the resume, showing the project name if available and implementation details. (NEVER use generic phrases like 'Found python directly in resume')",
      "confidence": 0.95
    }}
  ],
  "critical_gaps": [
    {{
      "skill": "Skill Name from JD",
      "importance": "CRITICAL",
      "note": "Reason why it is critical for backend/system development"
    }}
  ],
  "recommended_improvements": [
    {{
      "skill": "Skill Name from JD",
      "importance": "IMPORTANT",
      "note": "Reason why this improves capability"
    }}
  ],
  "optional_skills": [
    {{
      "skill": "Skill Name from JD",
      "importance": "OPTIONAL",
      "note": "Reason/Note (e.g. candidate already has Gemini API experience)"
    }}
  ],
  "project_experience": [
    {{
      "experience": "RAG Pipeline Experience | Vector Search Experience | LLM Integration Experience | Fine-Tuning Experience | Agentic Workflow Experience",
      "evidence": "Concrete phrase from resume projects showing design and implementation, checking action verbs.",
      "detected": true
    }}
  ],
  "candidate_level": {{
    "candidate_level": "AI Engineer Intern Candidate | Junior AI Engineer | Mid Level AI Engineer | Senior AI Engineer",
    "reason": "Detailed explanation evaluating project complexity, production deployment, architecture ownership, testing, cloud experience, and database design."
  }},
  "confidence": {{
    "confidence_score": 85,
    "confidence_level": "LOW | MEDIUM | HIGH"
  }},
  "strengths": [
    "Top 3-5 strong aspects of the candidate relative to the JD"
  ],
  "weaknesses": [
    "Top 3-5 gaps or weaker areas of the candidate relative to the JD"
  ],
  "explanation": "A 2-3 sentence plain-English summary of why the candidate is or is not a good fit, referencing key matches and gaps",
  "suggestions": [
    "2-3 actionable suggestions for the candidate to improve their profile for this role"
  ],
  "hiring_recommendation": "Strong Hire | Hire | Neutral | Weak Reject | Strong Reject"
}}

Normalisation Rules for Competency Categories (use these for 'skill' under 'matched_skills'):
1. Map OpenAI API, Gemini API, Claude API, Groq API, etc. to Category "LLM API Integration".
2. Map ChromaDB, Pinecone, FAISS, Weaviate, etc. to Category "Vector Database Experience".
3. Map FastAPI, Flask, Django, etc. to Category "Python Backend Development".
4. Map SentenceTransformer, Embedding Models, HuggingFace embeddings, etc. to Category "Embedding Experience".
5. Map React, Next.js, Vue, etc. to Category "Frontend Development".
6. Map Docker, Docker Compose, Kubernetes, etc. to Category "Containerization".
7. Map PyTorch, TensorFlow, Keras to Category "Deep Learning Frameworks".
8. Map PostgreSQL, MySQL, MongoDB to Category "Database Experience".
9. Map AWS, GCP, Azure to Category "Cloud Platform Experience".

Match Type Guidelines:
- EXACT_MATCH: Same technology exists (e.g. JD: Docker, Resume: Docker).
- EQUIVALENT_MATCH: Different tools but same competency category (e.g. JD: Flask, Resume: FastAPI). Also for Deep Learning frameworks (JD: PyTorch, Resume: TensorFlow).
- PARTIAL_MATCH: Candidate has related knowledge/category basics but lacks direct tool/production experience or the skill is mentioned in a non-project context.

Evidence Guidelines:
- Evidence MUST contain: project name if available, concrete sentence/context from resume, and implementation detail (e.g., "implemented X using Y").
- Look for action verbs like 'built', 'designed', 'implemented', 'optimized', 'deployed', 'integrated', 'architected', 'developed', 'automated', 'created', 'engineered', 'managed', 'led', 'pioneered', 'orchestrated', 'scaled'.
- NEVER output generic comments. If strong evidence is missing, the skill match confidence must decrease, and the evidence field should clearly state the limitation.

Seniority Evaluation Guidelines:
- AI Engineer Intern Candidate: Currently studying or very recent graduate, primary experience from internships or academic projects, limited production exposure.
- Junior AI Engineer: 0-2 years professional experience. Basic project experience, minor tool usage, might lack cloud/deployment ownership, focus on task execution.
- Mid Level AI Engineer: 2-5 years professional experience. Multiple projects, API integrations, testing/database usage, demonstrates independent problem-solving, but less architecture/scale ownership.
- Senior AI Engineer: 5+ years professional experience. Architecture ownership, designing scalable systems, production cloud deployment, strong testing practices, database design, leading projects.

Confidence Calculation Guidelines:
- High confidence (90-99%): Resume contains rich project context, implementation details, strong action verbs for most matched skills, and the JD is clear. PDF quality is excellent.
- Medium confidence (60-89%): Resume has some project context, but might be less detailed, or some skills are mentioned without strong evidence. JD might have some ambiguities. Minor PDF issues.
- Low confidence (0-59%): Resume mainly lists keywords without project context. Significant PDF quality issues, or JD is very vague. AI response itself was less reliable (e.g., needed heavy post-processing).

Explanation Fields Guidelines:
- strengths: List 3-5 specific, evidence-backed strengths of the candidate relative to the JD (e.g. "Proven RAG pipeline implementation with ChromaDB and Gemini API").
- weaknesses: List 3-5 specific gaps or weaker areas referencing JD requirements (e.g. "No experience with Docker or containerization shown in projects").
- explanation: 2-3 sentence plain-English summary covering overall fit, key matches, and critical gaps.
- suggestions: 2-3 concrete, actionable improvements the candidate could make (e.g. "Add a containerised deployment project using Docker and Kubernetes").
- hiring_recommendation: One of "Strong Hire", "Hire", "Neutral", "Weak Reject", or "Strong Reject" based on overall alignment.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return ONLY the JSON object. No markdown, no code fences, no extra text.
"""


def extract_skills(resume_text: str, jd_text: str) -> SkillExtractionResult:
    """
    Extract technical skills, classify importance, and detect project evidence.

    Args:
        resume_text: Plain text extracted from the resume PDF.
        jd_text: Raw job description text.

    Returns:
        SkillExtractionResult with normalized match details and evidence.
    """

    global gemini_generation_disabled_until
    settings = get_settings()
    try:
        payload = get_cached_extraction(resume_text, jd_text, PROMPT_VERSION, settings.gemini_extraction_model)
        if payload is not None:
            # get_cached_extraction already logs: "Skill extraction loaded from cache"
            pass
        else:
            # Check circuit breaker before hit
            if time.time() < gemini_generation_disabled_until:
                logger.warning("Gemini temporarily disabled due to quota limit")
                result = extract_skills_fallback(resume_text, jd_text)
                result.fallback_mode = True
                try:
                    result = post_process_extraction_result(result, resume_text, jd_text)
                except Exception as e:
                    logger.error(f"Error post-processing skills in extract_skills: {e}", exc_info=True)
                return result

            logger.info("Cache miss. Calling Gemini")
            prompt = GEMINI_EXTRACTION_PROMPT.format(
                resume_text=resume_text[:settings.gemini_resume_token_limit],  # guard token limit
                jd_text=jd_text[:settings.gemini_jd_token_limit],
            )

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
                logger.info(f"Calling Gemini API ({settings.gemini_extraction_model}) for skill extraction")
                client = genai.Client(api_key=settings.gemini_api_key)
                return client.models.generate_content(
                    model=settings.gemini_extraction_model,
                    contents=prompt,
                )

            response = _call_gemini_with_retry()
            raw_text = response.text.strip()
            payload = _parse_json_response(raw_text)
            
            # Cache the raw parsed payload dictionary
            set_cached_extraction(resume_text, jd_text, PROMPT_VERSION, settings.gemini_extraction_model, payload, source="gemini")
        
        # Parse into structured schemas
        raw_matched = payload.get("matched_skills", [])
        for x in raw_matched:
            if "category" not in x:
                x["category"] = x.get("skill", "")
        matched = [MatchedSkill(**x) for x in raw_matched]
        
        critical_gaps = [MissingSkill(**x) for x in payload.get("critical_gaps", [])]
        recommended_improvements = [MissingSkill(**x) for x in payload.get("recommended_improvements", [])]
        optional_skills = [MissingSkill(**x) for x in payload.get("optional_skills", [])]
        
        # Fallback if the new keys are empty but old missing_skills exists
        if not critical_gaps and not recommended_improvements and not optional_skills:
            for x in payload.get("missing_skills", []):
                ms = MissingSkill(**x)
                if ms.importance == IMPORTANCE_CRITICAL:
                    critical_gaps.append(ms)
                elif ms.importance == IMPORTANCE_IMPORTANT:
                    recommended_improvements.append(ms)
                else:
                    optional_skills.append(ms)
                    
        missing_skills = critical_gaps + recommended_improvements + optional_skills
        projects = [ProjectExperience(**x) for x in payload.get("project_experience", [])]
        
        # Candidate Level
        level_data = payload.get("candidate_level", {})
        candidate_level = None
        if level_data:
            candidate_level = CandidateLevel(
                candidate_level=level_data.get("candidate_level", "Mid Level Engineer"),
                reason=level_data.get("reason", "Assessment based on project experience and keywords.")
            )
            
        # Confidence
        conf_data = payload.get("confidence", {})
        confidence = None
        if conf_data:
            confidence = ConfidenceResult(
                confidence_score=conf_data.get("confidence_score", 75),
                confidence_level=conf_data.get("confidence_level", CONFIDENCE_MEDIUM)
            )
            
        result = SkillExtractionResult(
            matched_skills=matched,
            missing_skills=missing_skills,
            critical_gaps=critical_gaps,
            recommended_improvements=recommended_improvements,
            optional_skills=optional_skills,
            project_experience=projects,
            candidate_level=candidate_level,
            confidence=confidence,
            fallback_mode=payload.get("fallback_mode", False),
            strengths=payload.get("strengths", []),
            weaknesses=payload.get("weaknesses", []),
            explanation=payload.get("explanation", ""),
            suggestions=payload.get("suggestions", []),
            hiring_recommendation=payload.get("hiring_recommendation", ""),
        )
    except ClientError as exc:
        if exc.code == 429:
            logger.warning("Gemini quota exceeded. Local fallback activated.")
            # Set cooldown for 5 minutes
            gemini_generation_disabled_until = time.time() + 300
            
            # Use local fallback extractor
            result = extract_skills_fallback(resume_text, jd_text)
            result.fallback_mode = True
            
            # Cache the fallback result for 15 minutes (900 seconds)
            try:
                fallback_dict = {
                    "matched_skills": [m.model_dump() for m in result.matched_skills],
                    "critical_gaps": [m.model_dump() for m in result.critical_gaps],
                    "recommended_improvements": [m.model_dump() for m in result.recommended_improvements],
                    "optional_skills": [m.model_dump() for m in result.optional_skills],
                    "project_experience": [m.model_dump() for m in result.project_experience],
                    "candidate_level": result.candidate_level.model_dump() if result.candidate_level else None,
                    "confidence": result.confidence.model_dump() if result.confidence else None,
                    "strengths": result.strengths,
                    "weaknesses": result.weaknesses,
                    "explanation": result.explanation,
                    "suggestions": result.suggestions,
                    "hiring_recommendation": result.hiring_recommendation,
                    "fallback_mode": True
                }
                set_cached_extraction(resume_text, jd_text, PROMPT_VERSION, settings.gemini_extraction_model, fallback_dict, ttl_seconds=900, source="local_fallback")
            except Exception as cache_err:
                logger.warning(f"Failed to cache fallback extraction result: {cache_err}")
        elif exc.code in (401, 403):
            logger.warning("Gemini authentication failed.")
            result = extract_skills_fallback(resume_text, jd_text)
            result.fallback_mode = True
        else:
            logger.warning(
                f"Gemini ClientError ({exc.code}). Local fallback activated.",
                extra={"error": str(exc)}
            )
            result = extract_skills_fallback(resume_text, jd_text)
            result.fallback_mode = True
    except Exception as exc:
        logger.warning(
            "Gemini skill extraction failed. Falling back to local heuristic skill extractor.",
            extra={"error": str(exc)},
            exc_info=True
        )
        result = extract_skills_fallback(resume_text, jd_text)
        result.fallback_mode = True

    try:
        result = post_process_extraction_result(result, resume_text, jd_text) # Post-processing still applies to AI result
    except Exception as e:
        logger.error(f"Error post-processing skills in extract_skills: {e}", exc_info=True)

    logger.info(
        "Skills extracted",
        extra={
            "matched_count": len(result.matched_skills),
            "critical_gaps_count": len(result.critical_gaps),
            "recommended_improvements_count": len(result.recommended_improvements),
            "optional_skills_count": len(result.optional_skills),
            "project_exp_count": len(result.project_experience),
            "fallback_mode": result.fallback_mode,
        },
    )
    return result


def _parse_json_response(raw: str) -> dict[str, Any]:
    """
    Robustly parse JSON from Gemini output.
    Handles cases where the model wraps output in markdown code fences.
    """
    # Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    return json.loads(cleaned)

# Removed all helper functions and hardcoded lists that were moved to local_skill_extractor.py
