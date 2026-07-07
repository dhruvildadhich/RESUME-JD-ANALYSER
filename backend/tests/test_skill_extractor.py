"""
Tests for SkillExtractionService (unit — mocks Gemini).
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.analysis import SkillExtractionResult
from app.services.skill_extractor import extract_skills, _parse_json_response, extract_skills_fallback


class TestParseJsonResponse:
    def test_plain_json(self):
        raw = '{"resume_skills": ["python"], "jd_skills": ["java"]}'
        result = _parse_json_response(raw)
        assert result["resume_skills"] == ["python"]

    def test_with_markdown_fence(self):
        raw = '```json\n{"resume_skills": ["python"], "jd_skills": []}\n```'
        result = _parse_json_response(raw)
        assert result["resume_skills"] == ["python"]

    def test_with_plain_fence(self):
        raw = '```\n{"resume_skills": [], "jd_skills": ["go"]}\n```'
        result = _parse_json_response(raw)
        assert result["jd_skills"] == ["go"]

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("not json at all")


class TestExtractSkills:
    def _mock_gemini_response(self, payload: dict) -> MagicMock:
        mock_response = MagicMock()
        mock_response.text = json.dumps(payload)
        return mock_response

    def _setup_mock_client(self, mock_genai, payload: dict):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = self._mock_gemini_response(payload)
        mock_genai.Client.return_value = mock_client

    @patch("app.services.skill_extractor.genai")
    def test_successful_extraction(self, mock_genai):
        payload = {
            "matched_skills": [
                {
                    "skill": "Python Backend Development",
                    "required_skill": "Flask",
                    "candidate_skill": "FastAPI",
                    "match_type": "EQUIVALENT_MATCH",
                    "evidence": "Used FastAPI in Fashion Twin project",
                    "confidence": 0.90
                }
            ],
            "critical_gaps": [
                {"skill": "REST APIs", "importance": "CRITICAL", "note": "Required for backend design"}
            ],
            "recommended_improvements": [
                {"skill": "Docker", "importance": "IMPORTANT", "note": "Useful for deploy"}
            ],
            "optional_skills": [
                {"skill": "Claude", "importance": "OPTIONAL", "note": "Optional tool"}
            ],
            "project_experience": [
                {"experience": "RAG Pipeline Experience", "evidence": "Built document search", "detected": True}
            ],
            "candidate_level": {
                "candidate_level": "Mid Level Engineer",
                "reason": "Assess based on projects."
            },
            "confidence": {
                "confidence_score": 80,
                "confidence_level": "HIGH"
            }
        }
        self._setup_mock_client(mock_genai, payload)

        result = extract_skills("resume text here", "job desc here")

        assert isinstance(result, SkillExtractionResult)
        assert result.matched_skills[0].match_type in ("EQUIVALENT", "EQUIVALENT_MATCH")
        assert result.matched_skills[0].required_skill == "Flask"
        assert result.matched_skills[0].candidate_skill == "FastAPI"
        assert result.critical_gaps[0].skill == "REST APIs"
        assert result.recommended_improvements[0].skill == "Docker"
        assert result.optional_skills[0].skill == "Claude"
        assert result.candidate_level.candidate_level in ("Entry Level AI Engineer", "Mid Level Engineer", "Mid Level AI Engineer")
        assert result.confidence.confidence_score in (70, 80, 85)

    @patch("app.services.skill_extractor.genai")
    def test_fallback_mechanism(self, mock_genai):
        # Trigger an exception to test fallback code
        mock_genai.Client.side_effect = Exception("API Key Denied")
        
        result = extract_skills(
            "Python developer. Experienced in FastAPI and Docker. Built a RAG document search using ChromaDB.", 
            "We need a Python developer with FastAPI, Docker, and PyTorch."
        )
        assert isinstance(result, SkillExtractionResult)
        assert result.fallback_mode is True
        
        # Verify fallback rule-based matching worked
        matched_skills = [m.required_skill.lower() for m in result.matched_skills]
        assert "python" in matched_skills
        assert "fastapi" in matched_skills
        assert "docker" in matched_skills
        
        # Verify RAG project experience detected
        project_exps = [p.experience for p in result.project_experience if p.detected]
        assert "RAG Pipeline Experience" in project_exps

    def test_fallback_equivalent_skills_mapping(self):
        # Test 1: FastAPI matches Flask as equivalent
        result = extract_skills_fallback(
            resume_text="FastAPI developer with Python experience.",
            jd_text="Looking for a Python developer with Flask experience."
        )
        matched_eq = [m for m in result.matched_skills if m.match_type == "EQUIVALENT"]
        assert len(matched_eq) > 0
        assert any(m.required_skill == "Flask" and m.candidate_skill == "FastAPI" for m in matched_eq)

        # Test 2: Gemini API matches OpenAI API capability
        result2 = extract_skills_fallback(
            resume_text="Experienced with Gemini API and Google LLM models.",
            jd_text="Looking for someone with OpenAI API experience."
        )
        matched_eq2 = [m for m in result2.matched_skills if m.match_type == "EQUIVALENT"]
        assert len(matched_eq2) > 0
        assert any(m.required_skill == "OpenAI" and m.candidate_skill == "Gemini" for m in matched_eq2)

    def test_resume_groq_llama_jd_llm_expected_match(self):
        # 1. Resume: "Groq API + Llama 3.3", JD: "LLM", Expected: MATCH
        result = extract_skills_fallback(
            resume_text="Experienced in integrating Llama 3.3 70B inference using Groq API.",
            jd_text="Looking for an engineer with LLM experience."
        )
        matched_llm = [m for m in result.matched_skills if m.required_skill == "LLM"]
        assert len(matched_llm) > 0
        assert matched_llm[0].match_type == "EQUIVALENT"
        assert "Llama" in matched_llm[0].candidate_skill or "Groq" in matched_llm[0].candidate_skill

    def test_resume_pandas_jd_pandas_match(self):
        # 2. Resume: "Pandas", PDF text: "Pandas", Expected: MATCH
        result = extract_skills_fallback(
            resume_text="Data Analyst with Pandas experience.",
            jd_text="Required: experience with Pandas."
        )
        matched_pandas = [m for m in result.matched_skills if m.required_skill == "Pandas"]
        assert len(matched_pandas) > 0

    def test_student_with_strong_projects_seniority_evaluation(self):
        # Student with strong projects → AI Engineer Intern Candidate (NOT Senior Engineer)
        resume_text = """
        John Doe
        BE Student at Stanford University.
        Internship: AI Engineering Intern at Google.
        Projects: 
        - Built and deployed full-scale production RAG pipeline using FastAPI, ChromaDB, and Docker.
        - Deployed LLM agents with LangChain.
        """
        result = extract_skills_fallback(
            resume_text=resume_text,
            jd_text="Looking for a Senior AI Engineer."
        )
        assert result.candidate_level.candidate_level == "AI Engineer Intern Candidate"
        assert result.candidate_level.candidate_level != "Senior AI Engineer"

    def test_fallback_extraction_confidence(self):
        # 5. Fallback extraction -> confidence <= 85
        result = extract_skills_fallback(
            resume_text="FastAPI developer with Python experience.",
            jd_text="Flask developer."
        )
        assert result.fallback_mode is True
        assert result.confidence.confidence_score <= 85

