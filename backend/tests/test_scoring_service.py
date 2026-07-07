"""
Tests for ScoringService.
"""
import pytest

from app.schemas.analysis import ScoringResult, MatchedSkill, MissingSkill, ProjectExperience
from app.services.scoring_service import calculate_score


class TestCalculateScore:
    def test_perfect_match(self):
        matched = [
            MatchedSkill(skill="Python", category="Backend Development", evidence="Built production Python applications and deployed with Docker"),
            MatchedSkill(skill="FastAPI", category="Python Backend Development", evidence="Designed and implemented FastAPI-based microservices")
        ]
        projects = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Implemented full document search pipeline with vector embeddings", detected=True),
            ProjectExperience(experience="Vector Search Experience", evidence="Designed and built vector search indexing 10000 documents", detected=True),
            ProjectExperience(experience="LLM Integration Experience", evidence="Deployed LLM models to production with monitoring", detected=True)
        ]

        result = calculate_score(
            matched_skills=matched,
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=projects,
            semantic_similarity=1.0,
        )
        assert result.final_score >= 85
        assert result.skill_overlap_score == 100.0
        assert result.project_experience_score == 90.0

    def test_partial_match_ai_engineer_example(self):
        matched = [
            MatchedSkill(skill="Python Backend Development", category="Python Backend Development",
                         required_skill="FastAPI", candidate_skill="FastAPI",
                         match_type="EXACT_MATCH", evidence="Built production FastAPI API services", confidence=0.95),
            MatchedSkill(skill="LLM API Integration", category="LLM API Integration",
                         required_skill="Gemini", candidate_skill="Gemini",
                         match_type="EXACT_MATCH", evidence="Integrated Gemini API for document analysis", confidence=0.90),
            MatchedSkill(skill="RAG", category="RAG Pipeline",
                         required_skill="RAG", candidate_skill="RAG",
                         match_type="EXACT_MATCH", evidence="Designed RAG pipeline using embeddings and ChromaDB", confidence=0.90),
            MatchedSkill(skill="Vector Database Experience", category="Vector Database Experience",
                         required_skill="ChromaDB", candidate_skill="ChromaDB",
                         match_type="EXACT_MATCH", evidence="Implemented vector search with ChromaDB for 5000 items", confidence=0.85)
        ]
        critical_gaps = []
        recommended_improvements = [
            MissingSkill(skill="PyTorch", importance="IMPORTANT", note="Missing PyTorch")
        ]
        optional_skills = [
            MissingSkill(skill="AWS", importance="OPTIONAL", note="AWS is optional"),
            MissingSkill(skill="Claude", importance="OPTIONAL", note="Claude is optional")
        ]
        projects = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Built document search with FastAPI and ChromaDB", detected=True),
            ProjectExperience(experience="Vector Search Experience", evidence="Designed vector search pipeline", detected=True),
            ProjectExperience(experience="LLM Integration Experience", evidence="Integrated LLM API with Gemini", detected=True)
        ]

        result = calculate_score(
            matched_skills=matched,
            critical_gaps=critical_gaps,
            recommended_improvements=recommended_improvements,
            optional_skills=optional_skills,
            project_experience=projects,
            semantic_similarity=0.80,
        )
        assert 65 <= result.final_score <= 90

    def test_optional_missing_skills_low_penalty(self):
        matched = [
            MatchedSkill(skill="Python Backend Development", category="Python Backend Development",
                         required_skill="FastAPI", candidate_skill="FastAPI",
                         match_type="EXACT_MATCH", evidence="Implemented FastAPI backend", confidence=0.95),
            MatchedSkill(skill="Python Backend Development", category="Python Backend Development",
                         required_skill="Python", candidate_skill="Python",
                         match_type="EXACT_MATCH", evidence="Built Python data processing pipelines", confidence=0.95),
            MatchedSkill(skill="RAG Pipeline", category="RAG Pipeline",
                         required_skill="RAG", candidate_skill="RAG",
                         match_type="EXACT_MATCH", evidence="Implemented RAG system for document retrieval", confidence=0.90),
            MatchedSkill(skill="Vector Database Experience", category="Vector Database Experience",
                         required_skill="ChromaDB", candidate_skill="ChromaDB",
                         match_type="EXACT_MATCH", evidence="Integrated ChromaDB for vector search", confidence=0.85)
        ]
        optional_skills = [
            MissingSkill(skill="Claude", importance="OPTIONAL", note="Claude missing"),
            MissingSkill(skill="AWS", importance="OPTIONAL", note="AWS missing"),
            MissingSkill(skill="Azure", importance="OPTIONAL", note="Azure missing")
        ]
        projects = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Built RAG pipeline with FastAPI", detected=True),
            ProjectExperience(experience="Vector Search Experience", evidence="Implemented vector search for production", detected=True),
            ProjectExperience(experience="LLM Integration Experience", evidence="Integrated LLM APIs", detected=True)
        ]
        result = calculate_score(
            matched_skills=matched,
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=optional_skills,
            project_experience=projects,
            semantic_similarity=0.90,
        )
        assert result.final_score >= 75

    def test_learning_rag_vs_production_rag(self):
        matched = [MatchedSkill(skill="Python", category="Backend Development",
                                required_skill="Python", candidate_skill="Python",
                                match_type="EXACT_MATCH", evidence="Used Python in projects", confidence=0.80)]

        # Scenario A: Candidate is only "learning" RAG
        projects_learning = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Learning RAG and ChromaDB", detected=True)
        ]
        res_learning = calculate_score(
            matched_skills=matched,
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=projects_learning,
            semantic_similarity=0.5,
        )

        # Scenario B: Candidate "implemented" RAG in production
        projects_implemented = [
            ProjectExperience(experience="RAG Pipeline Experience", evidence="Implemented FastAPI and RAG pipeline with ChromaDB", detected=True)
        ]
        res_implemented = calculate_score(
            matched_skills=matched,
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=projects_implemented,
            semantic_similarity=0.5,
        )

        assert res_implemented.project_experience_score > res_learning.project_experience_score
        assert res_implemented.final_score > res_learning.final_score

    def test_no_match(self):
        result = calculate_score(
            matched_skills=[],
            critical_gaps=[MissingSkill(skill="Python", importance="CRITICAL", note="Missing")],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=[],
            semantic_similarity=0.0,
        )
        assert result.final_score == 0
        assert result.skill_overlap_score == 0.0
        assert result.project_experience_score == 0.0

    def test_return_type(self):
        result = calculate_score(
            matched_skills=[],
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=[],
            semantic_similarity=0.5,
        )
        assert isinstance(result, ScoringResult)

    def test_keyword_stuffing_vs_strong_projects(self):
        # Resume A: keyword stuffing - 7 skills listed but no project evidence
        stuffed = [
            MatchedSkill(skill="Python", category="Backend Development",
                         required_skill="Python", candidate_skill="Python",
                         match_type="EXACT_MATCH", evidence="Python", confidence=0.95),
            MatchedSkill(skill="Docker", category="Containerization",
                         required_skill="Docker", candidate_skill="Docker",
                         match_type="EXACT_MATCH", evidence="Docker", confidence=0.95),
            MatchedSkill(skill="AWS", category="Cloud",
                         required_skill="AWS", candidate_skill="AWS",
                         match_type="EXACT_MATCH", evidence="AWS", confidence=0.90),
            MatchedSkill(skill="LLM API Integration", category="LLM",
                         required_skill="OpenAI", candidate_skill="OpenAI",
                         match_type="EXACT_MATCH", evidence="OpenAI", confidence=0.90),
            MatchedSkill(skill="Deep Learning", category="Deep Learning",
                         required_skill="TensorFlow", candidate_skill="TensorFlow",
                         match_type="EXACT_MATCH", evidence="TensorFlow", confidence=0.85),
        ]
        result_stuffed = calculate_score(
            matched_skills=stuffed,
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=[],
            semantic_similarity=0.50,
        )

        # Resume B: strong project evidence - fewer skills but proven
        proven = [
            MatchedSkill(skill="RAG Pipeline", category="RAG",
                         required_skill="RAG", candidate_skill="RAG",
                         match_type="EXACT_MATCH", evidence="Built RAG pipeline indexing 26000 documents", confidence=0.95),
            MatchedSkill(skill="Vector Database Experience", category="Vector DB",
                         required_skill="ChromaDB", candidate_skill="ChromaDB",
                         match_type="EXACT_MATCH", evidence="Designed and deployed vector search with ChromaDB", confidence=0.95),
            MatchedSkill(skill="Python Backend Development", category="Backend",
                         required_skill="FastAPI", candidate_skill="FastAPI",
                         match_type="EXACT_MATCH", evidence="Built FastAPI backend with PostgreSQL and Docker", confidence=0.95),
        ]
        result_proven = calculate_score(
            matched_skills=proven,
            critical_gaps=[],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=[
                ProjectExperience(experience="RAG Pipeline Experience",
                                  evidence="Built RAG pipeline indexing 26000 documents with embeddings",
                                  detected=True),
                ProjectExperience(experience="Vector Search Experience",
                                  evidence="Designed vector search with ChromaDB, optimized for latency",
                                  detected=True),
                ProjectExperience(experience="LLM Integration Experience",
                                  evidence="Integrated Gemini API for real-time document analysis",
                                  detected=True),
            ],
            semantic_similarity=0.50,
        )

        assert result_proven.final_score > result_stuffed.final_score
        assert result_proven.project_experience_score > result_stuffed.project_experience_score

    def test_unknown_experience_no_midlevel_assumption(self):
        # Resume with no years/experience indicators — should not default to mid-level
        matched = [
            MatchedSkill(skill="Python", category="Backend",
                         required_skill="Python", candidate_skill="Python",
                         match_type="EXACT_MATCH", evidence="Used Python", confidence=0.80),
        ]
        result = calculate_score(
            matched_skills=matched,
            critical_gaps=[MissingSkill(skill="FastAPI", importance="CRITICAL", note="Missing")],
            recommended_improvements=[],
            optional_skills=[],
            project_experience=[],
            semantic_similarity=0.30,
        )
        # Without strong evidence and with critical gaps, score should be low
        assert result.final_score < 50
