"""
Unit tests for Gemini API reliability and caching optimizations.
"""
import json
import time
import sqlite3
from unittest.mock import MagicMock, patch
import pytest

from google.genai.errors import ClientError
from app.core.cache import CACHE_DB, initialize_cache
from app.schemas.analysis import SkillExtractionResult, MatchedSkill, MissingSkill
from app.services.skill_extractor import extract_skills
from app.services.ai_explanation import generate_explanation


@pytest.fixture(autouse=True)
def setup_clean_cache():
    """Ensure SQLite cache is initialized and clean before each test."""
    initialize_cache()
    # Clear cache tables
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM extractions")
    cursor.execute("DELETE FROM explanations")
    cursor.execute("DELETE FROM embeddings")
    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def reset_circuit_breaker():
    """Ensure circuit breaker cooldown is reset before each test."""
    from app.services import skill_extractor
    skill_extractor.gemini_generation_disabled_until = 0.0


class TestReliabilityOptimization:

    @patch("app.services.skill_extractor.genai")
    def test_gemini_429_immediately_falls_back_and_called_once(self, mock_genai):
        """Test that a 429 ClientError causes immediate fallback with exactly one attempt (no retry)."""
        # Create a mock client that raises ClientError with code 429
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = ClientError(429, {}, None)
        mock_genai.Client.return_value = mock_client

        # Call extraction
        result = extract_skills("Resume text", "Job Description")

        # Verify fallback is activated
        assert result.fallback_mode is True
        # Verify generate_content was called exactly once (no retry on 429)
        assert mock_client.models.generate_content.call_count == 1

    @patch("app.services.skill_extractor.genai")
    @patch("app.services.ai_explanation.genai")
    def test_cache_usage_on_repeated_requests(self, mock_genai_explanation, mock_genai_extractor):
        """Test that repeated requests use SQLite cache and don't hit the Gemini API."""
        # 1. Setup Mock for skill extraction
        mock_extractor_client = MagicMock()
        mock_extractor_resp = MagicMock()
        mock_extractor_resp.text = json.dumps({
            "matched_skills": [],
            "critical_gaps": [],
            "recommended_improvements": [],
            "optional_skills": [],
            "project_experience": [],
            "candidate_level": {"candidate_level": "Mid Level AI Engineer", "reason": "Test reason"},
            "confidence": {"confidence_score": 80, "confidence_level": "MEDIUM"}
        })
        mock_extractor_client.models.generate_content.return_value = mock_extractor_resp
        mock_genai_extractor.Client.return_value = mock_extractor_client

        # 2. Setup Mock for AI explanation
        mock_explanation_client = MagicMock()
        mock_explanation_resp = MagicMock()
        mock_explanation_resp.text = json.dumps({
            "strengths": ["Strength 1"],
            "weaknesses": ["Weakness 1"],
            "explanation": "professional narrative",
            "suggestions": ["Suggestion 1"],
            "hiring_recommendation": "Potential Match"
        })
        mock_explanation_client.models.generate_content.return_value = mock_explanation_resp
        mock_genai_explanation.Client.return_value = mock_explanation_client

        resume = "Some Candidate Resume Text"
        jd = "Some Candidate Job Description Text"

        # First Call (populates cache)
        res1 = extract_skills(resume, jd)
        assert res1.fallback_mode is False
        assert mock_extractor_client.models.generate_content.call_count == 1

        exp1 = generate_explanation(
            resume_text=resume,
            jd_text=jd,
            match_score=70,
            matched_skills=[],
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            extraction_result=res1
        )
        assert mock_explanation_client.models.generate_content.call_count == 1

        # Second Call (should hit cache)
        res2 = extract_skills(resume, jd)
        assert res2.fallback_mode is False
        # Call count should still be 1 (cache hit!)
        assert mock_extractor_client.models.generate_content.call_count == 1

        exp2 = generate_explanation(
            resume_text=resume,
            jd_text=jd,
            match_score=70,
            matched_skills=[],
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            extraction_result=res2
        )
        # Call count should still be 1 (cache hit!)
        assert mock_explanation_client.models.generate_content.call_count == 1

        # Verify results match
        assert exp2["hiring_recommendation"] == "Potential Match"

    @patch("app.services.ai_explanation.genai")
    def test_explanation_fallback_when_extraction_fallback_mode_is_true(self, mock_genai):
        """Test that if the skill extraction result has fallback_mode=True, the explanation skips Gemini and uses local heuristics."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        # Create a mock extraction result with fallback_mode = True
        extraction_result = SkillExtractionResult(
            matched_skills=[],
            missing_skills=[],
            fallback_mode=True
        )

        # Call explanation service
        result = generate_explanation(
            resume_text="Resume",
            jd_text="JD",
            match_score=50,
            matched_skills=[],
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            extraction_result=extraction_result
        )

        # Verify Gemini Client was never instantiated/called
        mock_genai.Client.assert_not_called()
        mock_client.models.generate_content.assert_not_called()

        # Verify fallback heuristic response fields are present
        assert "strengths" in result
        assert "weaknesses" in result
        assert "explanation" in result
        assert "suggestions" in result

    @patch("app.services.skill_extractor.genai")
    def test_circuit_breaker_prevents_subsequent_api_calls(self, mock_genai):
        """Test that a 429 quota error activates the circuit breaker, preventing subsequent calls to Gemini API."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = ClientError(429, {}, None)
        mock_genai.Client.return_value = mock_client

        # Call extraction (should trigger 429 and set cooldown)
        result1 = extract_skills("Resume Text A", "Job Desc A")
        assert result1.fallback_mode is True
        assert mock_client.models.generate_content.call_count == 1

        # Reset mock call count to track subsequent calls
        mock_client.models.generate_content.reset_mock()

        # Call extraction again with different texts (so cache doesn't hit)
        result2 = extract_skills("Resume Text B", "Job Desc B")
        assert result2.fallback_mode is True
        
        # Verify generate_content was NOT called because cooldown is active
        mock_client.models.generate_content.assert_not_called()

    @patch("app.services.embedding_service.get_settings")
    @patch("app.services.embedding_service.get_embedding_model")
    def test_embedding_cache_prevents_repeated_api_calls(self, mock_get_model, mock_get_settings):
        """Test that embedding cache prevents API calls for identical text on subsequent runs."""
        mock_settings = MagicMock()
        mock_settings.embedding_provider = "gemini"
        mock_settings.gemini_embedding_model = "models/embedding-001"
        mock_get_settings.return_value = mock_settings
        
        mock_client = MagicMock()
        mock_embed_response = MagicMock()
        
        # Setup mock embeddings return values
        mock_val = MagicMock()
        mock_val.values = [0.1, 0.2, 0.3]
        mock_embed_response.embeddings = [mock_val]
        mock_client.models.embed_content.return_value = mock_embed_response
        mock_get_model.return_value = mock_client

        from app.services.embedding_service import get_similarity
        
        # First similarity calculation
        sim1 = get_similarity("Resume Content", "Job Description Content")
        # Should call embed_content twice (one for resume, one for JD)
        assert mock_client.models.embed_content.call_count == 2

        # Reset mock call count
        mock_client.models.embed_content.reset_mock()

        # Second similarity calculation with same inputs
        sim2 = get_similarity("Resume Content", "Job Description Content")
        # Should call embed_content 0 times (both loaded from cache)
        mock_client.models.embed_content.assert_not_called()
        assert sim2 == sim1
