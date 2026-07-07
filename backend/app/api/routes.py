"""
API Routes — POST /api/analyze

Orchestrates the full resume-JD analysis pipeline:
  1. Parse PDF → extract text
  2. Extract skills from resume + JD via Gemini
  3. Compute embedding cosine similarity
  4. Calculate hybrid match score
  5. Generate AI explanation
"""

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.core.exceptions import FileSizeLimitError
from app.core.logging import get_logger
from app.schemas.analysis import AnalyzeResponse
from app.services.ai_explanation import generate_explanation
from app.services.embedding_service import get_similarity
from app.services.resume_parser import extract_text_from_pdf
from app.services.scoring_service import calculate_score
from app.services.skill_extractor import extract_skills

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyse resume against a job description",
    description=(
        "Upload a PDF resume and paste a job description. "
        "Returns a hybrid match score, skill breakdown, and AI-generated improvement suggestions."
    ),
)
async def analyze(
    resume: UploadFile = File(..., description="Candidate resume in PDF format"),
    jd_text: str = Form(..., min_length=50, description="Job description text (min 50 chars)"),
) -> AnalyzeResponse:
    """
    Full analysis pipeline endpoint.

    Multipart form:
      - resume: PDF file
      - jd_text: job description as plain text
    """
    settings = get_settings()

    # ── 1. Validate and read PDF ──────────────────────────────────────────────
    max_bytes = settings.max_pdf_size_mb * 1024 * 1024
    pdf_bytes = await resume.read()

    if len(pdf_bytes) > max_bytes:
        raise FileSizeLimitError(max_mb=settings.max_pdf_size_mb)

    logger.info(
        "Analysis request received",
        extra={"pdf_filename": resume.filename, "size_bytes": len(pdf_bytes)},
    )

    # ── 2. Extract resume text ────────────────────────────────────────────────
    resume_text = extract_text_from_pdf(pdf_bytes)

    # ── 3. Extract skills via Gemini ──────────────────────────────────────────
    skill_result = extract_skills(resume_text, jd_text)

    # ── 4. Compute semantic similarity ────────────────────────────────────────
    semantic_sim = get_similarity(resume_text, jd_text)

    # ── 5. Calculate hybrid score ─────────────────────────────────────────────
    scoring = calculate_score(
        matched_skills=skill_result.matched_skills,
        critical_gaps=skill_result.critical_gaps,
        recommended_improvements=skill_result.recommended_improvements,
        optional_skills=skill_result.optional_skills,
        project_experience=skill_result.project_experience,
        semantic_similarity=semantic_sim,
        candidate_level=skill_result.candidate_level,
        confidence=skill_result.confidence,
    )

    # ── 6. Generate AI explanation ────────────────────────────────────────────
    explanation_data = generate_explanation(
        resume_text=resume_text,
        jd_text=jd_text,
        match_score=scoring.final_score,
        matched_skills=scoring.matched_skills,
        critical_gaps=scoring.critical_gaps,
        recommended_improvements=scoring.recommended_improvements,
        optional_skills=scoring.optional_skills,
        extraction_result=skill_result,
    )

    response = AnalyzeResponse(
        match_score=scoring.final_score,
        matched_skills=scoring.matched_skills,
        missing_skills=scoring.missing_skills,
        critical_gaps=scoring.critical_gaps,
        recommended_improvements=scoring.recommended_improvements,
        optional_skills=scoring.optional_skills,
        project_experience=scoring.project_experience,
        candidate_level=scoring.candidate_level,
        confidence=scoring.confidence,
        strengths=explanation_data.get("strengths", []),
        weaknesses=explanation_data.get("weaknesses", []),
        explanation=explanation_data.get("explanation", ""),
        suggestions=explanation_data.get("suggestions", []),
        hiring_recommendation=explanation_data.get("hiring_recommendation", ""),
        skill_overlap_score=scoring.skill_overlap_score,
        semantic_similarity_score=scoring.semantic_similarity_score,
        project_experience_score=scoring.project_experience_score,
        bonus_score=scoring.bonus_score,
        fallback_mode=skill_result.fallback_mode,
    )

    logger.info(
        "Analysis complete",
        extra={
            "match_score": response.match_score,
            "hiring_recommendation": response.hiring_recommendation,
            "gemini_extraction_used": not skill_result.fallback_mode,
            "gemini_explanation_reused": bool(skill_result.explanation),
        },
    )
    return response
