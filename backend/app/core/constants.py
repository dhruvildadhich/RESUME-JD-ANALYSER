"""
Application-wide constants.

Single source of truth for reusable string literals, numeric thresholds,
and category mappings used across the Resume-JD Matcher backend.
"""

# ── Skill match types ─────────────────────────────────────────────────────────

EXACT_MATCH = "EXACT_MATCH"
EQUIVALENT_MATCH = "EQUIVALENT_MATCH"
PARTIAL_MATCH = "PARTIAL_MATCH"
EXACT = "EXACT"
EQUIVALENT = "EQUIVALENT"
PARTIAL = "PARTIAL"

MATCH_TYPE_CANONICAL = {
    EQUIVALENT_MATCH: EQUIVALENT,
    PARTIAL_MATCH: PARTIAL,
}

MATCH_TYPE_WEIGHTS = {
    EXACT_MATCH: 1.0,
    EXACT: 1.0,
    EQUIVALENT_MATCH: 0.75,
    EQUIVALENT: 0.75,
    PARTIAL_MATCH: 0.50,
    PARTIAL: 0.50,
}

# ── Skill importance levels ──────────────────────────────────────────────────

IMPORTANCE_CRITICAL = "CRITICAL"
IMPORTANCE_IMPORTANT = "IMPORTANT"
IMPORTANCE_OPTIONAL = "OPTIONAL"

IMPORTANCE_WEIGHTS = {
    IMPORTANCE_CRITICAL: 10.0,
    IMPORTANCE_IMPORTANT: 5.0,
    IMPORTANCE_OPTIONAL: 0.0,
}

# ── Confidence levels ────────────────────────────────────────────────────────

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"

# ── Hiring recommendations ───────────────────────────────────────────────────

RECOMMENDATION_EXCELLENT_MATCH = "Excellent Match"
RECOMMENDATION_STRONG_MATCH = "Strong Match"
RECOMMENDATION_POTENTIAL_MATCH = "Potential Match"
RECOMMENDATION_WEAK_MATCH = "Weak Match"

# ── Evidence scoring ─────────────────────────────────────────────────────────

EVIDENCE_MENTIONED_SCORE = 0.40
EVIDENCE_USED_SCORE = 0.70
EVIDENCE_BUILT_DEPLOYED_SCORE = 1.00

# ── Candidate levels ─────────────────────────────────────────────────────────

CANDIDATE_LEVEL_INTERN = "AI Engineer Intern Candidate"
CANDIDATE_LEVEL_JUNIOR = "Junior AI Engineer"
CANDIDATE_LEVEL_MID = "Mid Level AI Engineer"
CANDIDATE_LEVEL_SENIOR = "Senior AI Engineer"
CANDIDATE_LEVEL_ENTRY = "Entry Level AI Engineer"

# ── Experience levels (Evidence Validator) ────────────────────────────────────

EXPERIENCE_MENTION_ONLY = "Mention Only"
EXPERIENCE_PROJECT = "Project Experience"
EXPERIENCE_PRODUCTION = "Production Experience"

EXPERIENCE_CONFIDENCE = {
    EXPERIENCE_MENTION_ONLY: 50,
    EXPERIENCE_PROJECT: 80,
    EXPERIENCE_PRODUCTION: 95,
}

# ── Recruiter decisions ───────────────────────────────────────────────────────

RECRUITER_STRONG_CANDIDATE = "Strong Interview Candidate"
RECRUITER_POTENTIAL_CANDIDATE = "Potential Candidate"
RECRUITER_NEEDS_DEVELOPMENT = "Needs Development"

RECRUITER_RISK_LOW = "Low"
RECRUITER_RISK_MEDIUM = "Medium"
RECRUITER_RISK_HIGH = "High"

# ── Skill gap impact scores ───────────────────────────────────────────────────

IMPACT_CRITICAL = -25
IMPACT_IMPORTANT = -10
IMPACT_OPTIONAL = -5

# ── Evidence validator thresholds ────────────────────────────────────────────

EVIDENCE_CONFIDENCE_THRESHOLD = 0.50
EVIDENCE_CROSS_ENCODER_THRESHOLD = 0.65

# ── Confidence analysis thresholds ───────────────────────────────────────────

CONFIDENCE_HIGH_THRESHOLD = 90
CONFIDENCE_MEDIUM_THRESHOLD = 70

# ── Seniority evaluation thresholds ──────────────────────────────────────────

SENIORITY_YEARS_MAP = {
    CANDIDATE_LEVEL_INTERN: (0, 0.9),
    CANDIDATE_LEVEL_JUNIOR: (1, 2.9),
    CANDIDATE_LEVEL_MID: (3, 4.9),
    CANDIDATE_LEVEL_SENIOR: (5, 999),
}

# ── Production / bonus scoring ───────────────────────────────────────────────

PROD_BONUS_DOCKER = 20
PROD_BONUS_DOCKER_EVIDENCE = 10
PROD_BONUS_API = 15
PROD_BONUS_DATABASE = 15
PROD_BONUS_TESTING = 15
PROD_BONUS_CLOUD = 15
PROD_BONUS_CICD = 15
PROD_BONUS_MAX = 100.0

# ── Project experience scoring thresholds ────────────────────────────────────

PROJECT_SCORE_BUILT_AT_SCALE = 100.0
PROJECT_SCORE_BUILT = 85.0
PROJECT_SCORE_MIXED = 60.0
PROJECT_SCORE_LEARNING = 30.0
PROJECT_SCORE_CONTEXT = 60.0
PROJECT_SCORE_MINIMAL = 20.0
PROJECT_SCORE_NORMALIZATION_DIVISOR = 3.0

# ── Scoring final weights ────────────────────────────────────────────────────
# Weights are now managed in app.config.settings.Settings via .env

# ── Error message keys (API responses) ───────────────────────────────────────

ERROR_PDF_PARSE = "pdf_parse_error"
ERROR_GEMINI_API = "gemini_api_error"
ERROR_EMBEDDING = "embedding_error"
ERROR_FILE_TOO_LARGE = "file_too_large"
ERROR_INTERNAL = "internal_server_error"
