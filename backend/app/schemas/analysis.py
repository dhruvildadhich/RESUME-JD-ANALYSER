"""
Pydantic v2 schemas for the Resume-JD Matching API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of skill matches by importance."""
    critical_match: float = Field(..., description="Percentage of critical skills matched")
    important_match: float = Field(..., description="Percentage of important skills matched")
    optional_match: float = Field(..., description="Percentage of optional skills matched")
    semantic_score: float = Field(..., description="Overall semantic similarity score")


# ── NEW: Recruiter Intelligence Models ───────────────────────────────────────

class SkillEvidence(BaseModel):
    """Evidence validation result for a single skill."""
    skill_name: str = Field(..., description="The skill being validated")
    is_verified: bool = Field(..., description="True if evidence was found in resume")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    evidence_text: str = Field(default="", description="The actual text evidence found in resume")
    evidence_section: str = Field(default="", description="Resume section where evidence was found")
    experience_level: str = Field(default="Mention Only", description="Mention Only | Project Experience | Production Experience")


class ConfidenceAnalysis(BaseModel):
    """Granular analysis confidence with human-readable reasons."""
    confidence_score: int = Field(..., ge=0, le=100, description="Overall analysis confidence (0-100)")
    level: str = Field(..., description="HIGH | MEDIUM | LOW")
    reasons: List[str] = Field(default_factory=list, description="Human-readable reasons for this confidence level")


class RecruiterDecision(BaseModel):
    """Final recruiter-style hiring decision."""
    decision: str = Field(..., description="Strong Interview Candidate | Potential Candidate | Needs Development")
    risk_level: str = Field(..., description="Low | Medium | High")
    reasons: List[str] = Field(default_factory=list, description="3-bullet rationale for this decision")
    candidate_level: str = Field(default="", description="Seniority level label")


class ImprovementSuggestion(BaseModel):
    """A concrete, actionable resume improvement suggestion."""
    missing_skill: str = Field(..., description="The missing skill this suggestion addresses")
    suggestion: str = Field(..., description="Specific actionable text for the candidate's resume")
    priority: str = Field(..., description="CRITICAL | IMPORTANT | OPTIONAL")


# ── Structured models for upgraded matching ──────────────────────────────────

class MatchedSkill(BaseModel):
    """A technical skill matched between the resume and job description."""

    skill: str = Field(..., description="Normalized name of the skill")
    category: str = Field(..., description="Normalized competency category (e.g. LLM API Integration)")
    evidence: str = Field(..., description="Concrete context or evidence from the resume")
    required_skill: Optional[str] = Field(default=None, description="The skill name requested in JD")
    candidate_skill: Optional[str] = Field(default=None, description="The specific skill found in candidate resume")
    match_type: str = Field(default="EXACT_MATCH", description="EXACT_MATCH, EQUIVALENT_MATCH, PARTIAL_MATCH")
    importance: str = Field(default="IMPORTANT", description="Importance classification: CRITICAL, IMPORTANT, OPTIONAL")
    confidence: float = Field(default=1.0, description="Confidence of this specific skill match (0-1)")
    experience_level: Optional[str] = Field(default=None, description="Mention Only | Project Experience | Production Experience")


class MissingSkill(BaseModel):
    """A required skill that was not found in the candidate's resume."""

    skill: str = Field(..., description="Normalized name of the skill")
    importance: str = Field(..., description="Importance classification: CRITICAL, IMPORTANT, OPTIONAL")
    note: str = Field(..., description="Contextual note or suggestion (e.g. equivalent tools used)")
    reason: Optional[str] = Field(default=None, description="Reason why this skill is missing or important")
    suggestion: Optional[str] = Field(default=None, description="Actionable suggestion for the candidate")
    impact_score: Optional[int] = Field(default=None, description="Score impact of this missing skill (negative int)")


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
    skill_semantic_score: float = Field(default=0.0, ge=0.0, le=100.0)
    project_semantic_score: float = Field(default=0.0, ge=0.0, le=100.0)
    experience_semantic_score: float = Field(default=0.0, ge=0.0, le=100.0)
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
    score_breakdown: Optional[ScoreBreakdown] = None
    # Recruiter intelligence additions
    confidence_analysis: Optional[ConfidenceAnalysis] = None
    recruiter_decision: Optional[RecruiterDecision] = None
    unverified_skills: List[SkillEvidence] = Field(default_factory=list)
    improvement_plan: List[ImprovementSuggestion] = Field(default_factory=list)


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
    score_breakdown: Optional[ScoreBreakdown] = None
    strengths: List[str] = Field(default_factory=list, description="Top strengths of candidate")
    weaknesses: List[str] = Field(default_factory=list, description="Gaps or areas for improvement")
    explanation: str = Field(default="", description="AI recruiter summary explanation")
    suggestions: List[str] = Field(default_factory=list, description="Actionable improvement tips")
    
    # Detailed semantic scores
    skill_semantic_score: float = Field(default=0.0, description="Semantic similarity of technical skills")
    project_semantic_score: float = Field(default=0.0, description="Semantic similarity of project experience")
    experience_semantic_score: float = Field(default=0.0, description="Semantic similarity of general experience")
    final_semantic_score: float = Field(default=0.0, description="Overall weighted semantic similarity")
    hiring_recommendation: str = Field(..., description="AI hiring recommendation verdict")
    skill_overlap_score: float = Field(..., description="Raw skill-overlap component (0-100)")
    semantic_similarity_score: float = Field(..., description="Semantic similarity component (0-100)")
    project_experience_score: float = Field(..., description="Project experience component (0-100)")
    bonus_score: float = Field(..., description="Bonus skills component (0-100)")
    fallback_mode: Optional[bool] = Field(default=False, description="True if local heuristics fallback was used")
    # Recruiter intelligence additions
    confidence_analysis: Optional[ConfidenceAnalysis] = None
    recruiter_decision: Optional[RecruiterDecision] = None
    unverified_skills: List[SkillEvidence] = Field(default_factory=list, description="Skills with low evidence confidence")
    improvement_plan: List[ImprovementSuggestion] = Field(default_factory=list, description="Structured improvement suggestions")

