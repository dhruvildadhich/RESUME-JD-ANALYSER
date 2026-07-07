"""
API Routes — POST /api/analyze

Orchestrates the full resume-JD analysis pipeline:
  1. Parse PDF → extract text
  2. Extract skills from resume + JD via Gemini
  3. Compute embedding cosine similarity
  4. Calculate hybrid match score
  5. Generate AI explanation
"""

import asyncio
import time
from fastapi import APIRouter, File, Form, UploadFile, Body
from fastapi.responses import JSONResponse, StreamingResponse

from app.config.settings import get_settings
from app.core.exceptions import FileSizeLimitError
from app.core.logging import get_logger
from app.schemas.analysis import AnalyzeResponse
from app.services.ai_explanation import generate_explanation
from app.services.embedding_service import get_similarity
from app.services.resume_parser import extract_text_from_pdf
from app.services.scoring_service import calculate_score
from app.services.skill_extractor import extract_skills
from app.services.report_service import generate_analysis_report
from app.services.analysis_validator import validate_and_refine_analysis
from app.services.evidence_validator import validate_skills
from app.services.confidence_service import compute_confidence
from app.services.improvement_service import generate_improvements
from app.services.recruiter_service import make_decision
from app.core.constants import (
    RECOMMENDATION_EXCELLENT_MATCH,
    RECOMMENDATION_STRONG_MATCH,
    RECOMMENDATION_POTENTIAL_MATCH,
    RECOMMENDATION_WEAK_MATCH,
    IMPACT_CRITICAL,
    IMPACT_IMPORTANT,
    IMPACT_OPTIONAL,
    ERROR_PDF_PARSE,)

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
    start_total = time.time()
    settings = get_settings()

    # ── 1. Validate and read PDF ──────────────────────────────────────────────
    start_parse = time.time()
    max_bytes = settings.max_pdf_size_mb * 1024 * 1024
    pdf_bytes = await resume.read()

    if len(pdf_bytes) > max_bytes:
        raise FileSizeLimitError(max_mb=settings.max_pdf_size_mb)

    logger.info(
        "Analysis request received",
        extra={"pdf_filename": resume.filename, "size_bytes": len(pdf_bytes)},
    )

    # ── 2. Extract resume text ────────────────────────────────────────────────
    resume_text = await asyncio.to_thread(extract_text_from_pdf, pdf_bytes)
    parse_time = time.time() - start_parse

    # ── 3 & 4. Parallelize Gemini Extraction & Semantic Similarity ────────────
    start_parallel = time.time()
    
    skill_task = asyncio.create_task(
        asyncio.to_thread(extract_skills, resume_text, jd_text)
    )
    semantic_task = asyncio.create_task(
        asyncio.to_thread(get_similarity, resume_text, jd_text)
    )
    
    skill_result, semantic_sim = await asyncio.gather(skill_task, semantic_task)
    parallel_time = time.time() - start_parallel

    # We cannot exactly separate Gemini and Embedding times easily here since they run in parallel,
    # but we can log them as a combined "parallel_time" or assume they took roughly parallel_time.
    gemini_time = parallel_time
    embedding_time = parallel_time

    # ── 5. Calculate hybrid score ─────────────────────────────────────────────
    start_score = time.time()
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

    # ── 5b. AI Reviewer Validation ────────────────────────────────────────────
    scoring = validate_and_refine_analysis(
        resume_text=resume_text,
        jd_text=jd_text,
        extraction_result=skill_result,
        scoring_result=scoring
    )

    # ── 5c. Evidence Validation & Experience Classification ───────────────────
    enriched_matched, unverified_skills = await asyncio.to_thread(
        validate_skills,
        scoring.matched_skills,
        resume_text,
    )
    scoring.matched_skills = enriched_matched

    # ── 5d. Inject impact_score into missing skills ───────────────────────────
    for gap in scoring.critical_gaps:
        gap.impact_score = IMPACT_CRITICAL
    for imp in scoring.recommended_improvements:
        imp.impact_score = IMPACT_IMPORTANT
    for opt in scoring.optional_skills:
        opt.impact_score = IMPACT_OPTIONAL
    scoring.missing_skills = scoring.critical_gaps + scoring.recommended_improvements + scoring.optional_skills

    # ── 5e. Compute Analysis Confidence ──────────────────────────────────────
    confidence_analysis = compute_confidence(
        matched_skills=scoring.matched_skills,
        unverified_skills=unverified_skills,
        project_experience=scoring.project_experience,
        semantic_similarity_score=scoring.semantic_similarity_score,
    )

    # ── 5f. Generate Improvement Plan ────────────────────────────────────────
    improvement_plan = generate_improvements(
        critical_gaps=scoring.critical_gaps,
        recommended_improvements=scoring.recommended_improvements,
        optional_skills=scoring.optional_skills,
    )

    # ── 5g. Recruiter Decision ────────────────────────────────────────────────
    recruiter_decision = make_decision(
        final_score=scoring.final_score,
        matched_skills=scoring.matched_skills,
        critical_gaps=scoring.critical_gaps,
        recommended_improvements=scoring.recommended_improvements,
        candidate_level=scoring.candidate_level,
        confidence_analysis=confidence_analysis,
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
        score_breakdown=scoring.score_breakdown.model_dump() if scoring.score_breakdown else None,
        extraction_result=skill_result,
    )

    # ── 7. Calculate deterministic hiring recommendation ──────────────────────────
    if scoring.final_score >= 90:
        hiring_rec = RECOMMENDATION_EXCELLENT_MATCH
    elif scoring.final_score >= 80:
        hiring_rec = RECOMMENDATION_STRONG_MATCH
    elif scoring.final_score >= 65:
        hiring_rec = RECOMMENDATION_POTENTIAL_MATCH
    else:
        hiring_rec = RECOMMENDATION_WEAK_MATCH
        
    score_time = time.time() - start_score
    total_time = time.time() - start_total

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
        hiring_recommendation=hiring_rec,
        skill_overlap_score=scoring.skill_overlap_score,
        semantic_similarity_score=scoring.semantic_similarity_score,
        skill_semantic_score=scoring.skill_semantic_score,
        project_semantic_score=scoring.project_semantic_score,
        experience_semantic_score=scoring.experience_semantic_score,
        final_semantic_score=scoring.semantic_similarity_score,
        project_experience_score=scoring.project_experience_score,
        bonus_score=scoring.bonus_score,
        fallback_mode=skill_result.fallback_mode,
        score_breakdown=scoring.score_breakdown,
        # Recruiter intelligence
        confidence_analysis=confidence_analysis,
        recruiter_decision=recruiter_decision,
        unverified_skills=unverified_skills,
        improvement_plan=improvement_plan,
    )

    logger.info(
        f"Analysis completed: parse={parse_time:.1f}s gemini={gemini_time:.1f}s embedding={embedding_time:.1f}s scoring={score_time:.1f}s total={total_time:.1f}s",
        extra={
            "match_score": response.match_score,
            "hiring_recommendation": response.hiring_recommendation,
            "gemini_extraction_used": not skill_result.fallback_mode,
            "gemini_explanation_reused": bool(skill_result.explanation),
        },
    )
    return response


@router.post(
    "/report/download",
    summary="Download Analysis Report",
    description="Generates a PDF report from the analysis response payload.",
)
async def download_report(data: AnalyzeResponse = Body(...)):
    """
    Takes an existing AnalyzeResponse payload and generates a professional PDF report.
    """
    logger.info("Generating PDF report")
    
    # Generate the PDF buffer
    pdf_buffer = generate_analysis_report(data)
    
    # Return as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="AI_Recruiter_Report.pdf"'
        }
    )
