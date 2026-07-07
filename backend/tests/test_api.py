"""
Integration tests for POST /api/analyze.
Uses httpx.AsyncClient against the FastAPI test app.
All external calls (Gemini, embedding model) are mocked.
"""
import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.analysis import (
    SkillExtractionResult,
    ScoringResult,
    MatchedSkill,
    MissingSkill,
    ProjectExperience,
    CandidateLevel,
    ConfidenceResult,
)


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """
    Minimal valid single-page PDF containing the word 'Python developer'.
    Constructed from raw PDF syntax to avoid requiring a file on disk.
    """
    content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 44>>
stream
BT /F1 12 Tf 100 700 Td (Python developer resume) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000360 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
441
%%EOF"""
    return content


@pytest.mark.asyncio
class TestAnalyzeEndpoint:
    @patch("app.api.routes.generate_explanation")
    @patch("app.api.routes.calculate_score")
    @patch("app.api.routes.get_similarity")
    @patch("app.api.routes.extract_skills")
    @patch("app.api.routes.extract_text_from_pdf")
    async def test_successful_analysis(
        self,
        mock_parse,
        mock_extract,
        mock_similarity,
        mock_score,
        mock_explain,
        sample_pdf_bytes,
    ):
        # Arrange mocks
        mock_parse.return_value = "Python developer with 3 years experience"
        
        matched = [
            MatchedSkill(
                skill="Python Backend Development",
                required_skill="FastAPI",
                candidate_skill="FastAPI",
                match_type="EXACT_MATCH",
                category="Python Backend Development",
                evidence="FastAPI backend experience",
                confidence=0.95
            ),
        ]
        critical_gaps = [
            MissingSkill(skill="Docker", importance="CRITICAL", note="Docker is critical")
        ]
        recommended_improvements = []
        optional_skills = []
        missing = critical_gaps + recommended_improvements + optional_skills
        
        projects = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Built document search", detected=True)
        ]
        candidate_level = CandidateLevel(candidate_level="Mid Level Engineer", reason="Mid-level software indicators.")
        confidence = ConfidenceResult(confidence_score=80, confidence_level="HIGH")

        mock_extract.return_value = SkillExtractionResult(
            matched_skills=matched,
            missing_skills=missing,
            critical_gaps=critical_gaps,
            recommended_improvements=recommended_improvements,
            optional_skills=optional_skills,
            project_experience=projects,
            candidate_level=candidate_level,
            confidence=confidence,
            fallback_mode=False
        )
        mock_similarity.return_value = 0.85
        
        mock_score.return_value = ScoringResult(
            skill_overlap_score=66.67,
            semantic_similarity_score=85.0,
            project_experience_score=33.33,
            bonus_score=0.0,
            final_score=74,
            matched_skills=matched,
            missing_skills=missing,
            critical_gaps=critical_gaps,
            recommended_improvements=recommended_improvements,
            optional_skills=optional_skills,
            project_experience=projects,
            candidate_level=candidate_level,
            confidence=confidence,
        )
        mock_explain.return_value = {
            "strengths": ["Strong Python skills"],
            "weaknesses": ["Missing Docker experience"],
            "explanation": "Candidate is a good fit.",
            "suggestions": ["Learn Docker", "Build a containerised project"],
            "hiring_recommendation": "Good Potential Match",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/analyze",
                files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
                data={"jd_text": "We need a Python developer with FastAPI and Docker skills " * 3},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["match_score"] == 74
        assert data["matched_skills"][0]["skill"] == "Python Backend Development"
        assert data["critical_gaps"][0]["skill"] == "Docker"
        assert data["candidate_level"]["candidate_level"] == "Mid Level Engineer"
        assert data["confidence"]["confidence_score"] == 80
        assert data["hiring_recommendation"] == "Good Potential Match"

    @patch("app.services.ai_explanation.genai.Client")
    @patch("app.api.routes.calculate_score")
    @patch("app.api.routes.get_similarity")
    @patch("app.api.routes.extract_skills")
    @patch("app.api.routes.extract_text_from_pdf")
    async def test_explanation_reused_from_extraction(
        self,
        mock_parse,
        mock_extract,
        mock_similarity,
        mock_score,
        mock_gemini_client,
        sample_pdf_bytes,
    ):
        mock_parse.return_value = "Python developer with 3 years experience"

        matched = [
            MatchedSkill(
                skill="Python Backend Development",
                required_skill="FastAPI",
                candidate_skill="FastAPI",
                match_type="EXACT_MATCH",
                category="Python Backend Development",
                evidence="FastAPI backend experience",
                confidence=0.95,
            ),
        ]
        critical_gaps = [
            MissingSkill(skill="Docker", importance="CRITICAL", note="Docker is critical")
        ]
        projects = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Built document search", detected=True)
        ]
        candidate_level = CandidateLevel(candidate_level="Mid Level Engineer", reason="Mid-level software indicators.")
        confidence = ConfidenceResult(confidence_score=80, confidence_level="HIGH")

        # SkillExtractionResult with explanation data pre-populated
        mock_extract.return_value = SkillExtractionResult(
            matched_skills=matched,
            missing_skills=critical_gaps,
            critical_gaps=critical_gaps,
            recommended_improvements=[],
            optional_skills=[],
            project_experience=projects,
            candidate_level=candidate_level,
            confidence=confidence,
            fallback_mode=False,
            strengths=["Strong Python skills"],
            weaknesses=["Missing Docker experience"],
            explanation="Candidate is a good fit.",
            suggestions=["Learn Docker", "Build a containerised project"],
            hiring_recommendation="Good Potential Match",
        )
        mock_similarity.return_value = 0.85

        mock_score.return_value = ScoringResult(
            skill_overlap_score=66.67,
            semantic_similarity_score=85.0,
            project_experience_score=33.33,
            bonus_score=0.0,
            final_score=74,
            matched_skills=matched,
            missing_skills=critical_gaps,
            critical_gaps=critical_gaps,
            recommended_improvements=[],
            optional_skills=[],
            project_experience=projects,
            candidate_level=candidate_level,
            confidence=confidence,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/analyze",
                files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
                data={"jd_text": "We need a Python developer with FastAPI and Docker skills " * 3},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["match_score"] == 74
        assert data["explanation"] == "Candidate is a good fit."
        assert data["hiring_recommendation"] == "Good Potential Match"
        assert data["strengths"] == ["Strong Python skills"]
        assert data["suggestions"] == ["Learn Docker", "Build a containerised project"]
        # Gemini client should NOT be called since explanation is reused from extraction
        mock_gemini_client.assert_not_called()

    async def test_missing_jd_text_returns_422(self, sample_pdf_bytes):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/analyze",
                files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
                # jd_text intentionally omitted
            )
        assert response.status_code == 422

    async def test_health_endpoint(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
