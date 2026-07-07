"""
Pydantic v2 schemas for the Resume-JD Matching API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Structured models for upgraded matching ──────────────────────────────────

class MatchedSkill(BaseModel):
    """A technical skill matched between the resume and job description."""

    skill: str = Field(..., description="Normalized name of the skill")
    category: str = Field(..., description="Normalized competency category (e.g. LLM API Integration)")
    evidence: str = Field(..., description="Concrete context or evidence from the resume")
    required_skill: Optional[str] = Field(default=None, description="The skill name requested in JD")
    candidate_skill: Optional[str] = Field(default=None, description="The specific skill found in candidate resume")
    match_type: str = Field(default="EXACT_MATCH", description="EXACT_MATCH, EQUIVALENT_MATCH, PARTIAL_MATCH")
    confidence: float = Field(default=1.0, description="Confidence of this specific skill match (0-1)")


class MissingSkill(BaseModel):
    """A required skill that was not found in the candidate's resume."""

    skill: str = Field(..., description="Normalized name of the skill")
    importance: str = Field(..., description="Importance classification: CRITICAL, IMPORTANT, OPTIONAL")
    note: str = Field(..., description="Contextual note or suggestion (e.g. equivalent tools used)")


class ProjectExperience(BaseModel):
    """High-level AI or system architecture pattern detected in resume projects."""

    experience: str = Field(..., description="The experience pattern (e.g. RAG Pipeline Experience)")
    evidence: str = Field(..., description="Textual evidence from the resume showing this experience")
    detected: bool = Field(default=False, description="True if this experience pattern was found")


class CandidateLevel(BaseModel):
    """Assessment of the candidate's seniority level."""

    candidate_level: str = Field(..., description="Beginner, Junior Engineer, Mid Level Engineer, Senior Engineer")
    reason: str = Field(..., description="Detailed narrative reason explaining the seniority evaluation")


class ConfidenceResult(BaseModel):
    """Overall evaluation confidence metric."""

    confidence_score: int = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    confidence_level: str = Field(..., description="LOW, MEDIUM, HIGH")


# ── Internal models ──────────────────────────────────────────────────────────

class SkillExtractionResult(BaseModel):
    """Output of the Gemini skill-extraction call."""

    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    missing_skills: List[MissingSkill] = Field(default_factory=list)
    critical_gaps: List[MissingSkill] = Field(default_factory=list)
    recommended_improvements: List[MissingSkill] = Field(default_factory=list)
    optional_skills: List[MissingSkill] = Field(default_factory=list)
    project_experience: List[ProjectExperience] = Field(default_factory=list)
    candidate_level: Optional[CandidateLevel] = None
    confidence: Optional[ConfidenceResult] = None
    fallback_mode: bool = False
    # Explanation fields (populated by Gemini extraction to avoid a second API call)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    explanation: str = ""
    suggestions: List[str] = Field(default_factory=list)
    hiring_recommendation: str = ""


class ScoringResult(BaseModel):
    """Score breakdown computed by the scoring service."""

    skill_overlap_score: float = Field(..., ge=0.0, le=100.0)
    semantic_similarity_score: float = Field(..., ge=0.0, le=100.0)
    project_experience_score: float = Field(..., ge=0.0, le=100.0)
    bonus_score: float = Field(..., ge=0.0, le=100.0)
    final_score: int = Field(..., ge=0, le=100)
    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    missing_skills: List[MissingSkill] = Field(default_factory=list)
    critical_gaps: List[MissingSkill] = Field(default_factory=list)
    recommended_improvements: List[MissingSkill] = Field(default_factory=list)
    optional_skills: List[MissingSkill] = Field(default_factory=list)
    project_experience: List[ProjectExperience] = Field(default_factory=list)
    candidate_level: Optional[CandidateLevel] = None
    confidence: Optional[ConfidenceResult] = None


# ── API response ──────────────────────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """Public API response for POST /api/analyze."""

    match_score: int = Field(..., ge=0, le=100, description="Overall match percentage (0-100)")
    matched_skills: List[MatchedSkill] = Field(default_factory=list, description="Skills present in both resume and JD with evidence")
    missing_skills: List[MissingSkill] = Field(default_factory=list, description="JD skills absent from the resume")
    critical_gaps: List[MissingSkill] = Field(default_factory=list, description="Critical missing skills")
    recommended_improvements: List[MissingSkill] = Field(default_factory=list, description="Important missing skills")
    optional_skills: List[MissingSkill] = Field(default_factory=list, description="Optional missing skills")
    project_experience: List[ProjectExperience] = Field(default_factory=list, description="Architectural experience patterns detected")
    candidate_level: Optional[CandidateLevel] = None
    confidence: Optional[ConfidenceResult] = None
    strengths: List[str] = Field(default_factory=list, description="Candidate's highlighted strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Areas the candidate should improve")
    explanation: str = Field(..., description="AI-generated narrative analysis")
    suggestions: List[str] = Field(default_factory=list, description="Actionable resume improvement tips")
    hiring_recommendation: str = Field(..., description="AI hiring recommendation verdict")
    skill_overlap_score: float = Field(..., description="Raw skill-overlap component (0-100)")
    semantic_similarity_score: float = Field(..., description="Semantic similarity component (0-100)")
    project_experience_score: float = Field(..., description="Project experience component (0-100)")
    bonus_score: float = Field(..., description="Bonus skills component (0-100)")
    fallback_mode: Optional[bool] = Field(default=False, description="True if local heuristics fallback was used")

