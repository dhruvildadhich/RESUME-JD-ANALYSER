# Backend Service

FastAPI-based AI analysis engine for the Resume–JD Matcher platform. Accepts a PDF resume and job description text, runs them through a multi-stage AI pipeline, and returns a structured JSON evaluation including a match score, skill evidence, gap analysis, recruiter decision, confidence rating, and downloadable PDF report.

---

## Table of Contents

- [Requirements](#requirements)
- [Architecture](#architecture)
- [AI Pipeline](#ai-pipeline)
- [Service Reference](#service-reference)
- [API Endpoints](#api-endpoints)
- [Pydantic Schema Reference](#pydantic-schema-reference)
- [Environment Variables](#environment-variables)
- [Setup and Running](#setup-and-running)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [Performance Optimisations](#performance-optimisations)

---

## Requirements

| Package | Min Version | Purpose |
|---|---|---|
| Python | 3.10 | Runtime (3.12 recommended) |
| fastapi | 0.111.1 | Async REST API framework |
| uvicorn[standard] | 0.30.1 | ASGI server |
| pydantic | 2.7.4 | Schema validation and serialisation |
| pydantic-settings | 2.3.4 | Environment-based configuration |
| python-multipart | 0.0.9 | Multipart file upload parsing |
| google-generativeai | 0.8.3 | Gemini LLM + embedding API client |
| PyMuPDF | 1.28.0 | PDF text extraction |
| sentence-transformers | 3.0.0 | Local embeddings + cross-encoder reranking |
| torch | 2.0.0 | SentenceTransformer runtime |
| numpy | 2.0.0 | Vector and cosine similarity operations |
| reportlab | 4.2.0 | PDF report generation |
| python-json-logger | 2.0.7 | Structured JSON log output |
| python-dotenv | 1.0.1 | `.env` file loading |
| pytest | 8.2.2 | Test framework |
| pytest-asyncio | 0.23.7 | Async test support |
| httpx | 0.27.0 | Async HTTP client for integration tests |

---

## Architecture

```
backend/
├── app/
│   ├── main.py                       # App factory, lifespan, CORS, global exception handler
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                 # POST /api/analyze, POST /api/report/download
│   ├── config/
│   │   └── settings.py               # pydantic-settings — all env vars with defaults
│   ├── core/
│   │   ├── cache.py                  # SQLite cache (extraction + explanation responses)
│   │   ├── constants.py              # Match types, importance levels, scoring thresholds
│   │   ├── exceptions.py             # FileSizeLimitError, custom exception hierarchy
│   │   ├── logging.py                # JSON logging setup (get_logger, setup_logging)
│   │   └── skill_ontology.py         # Skill synonym and equivalence mappings
│   ├── schemas/
│   │   └── analysis.py               # All Pydantic models — request/response + DTOs
│   └── services/
│       ├── resume_parser.py          # PDF text extraction (PyMuPDF)
│       ├── skill_extractor.py        # Gemini LLM extraction + cache + fallback dispatch
│       ├── local_skill_extractor.py  # Keyword/regex NLP fallback pipeline
│       ├── embedding_service.py      # Gemini + BGE embeddings, cosine similarity
│       ├── reranker_service.py       # Cross-encoder singleton (ms-marco-MiniLM-L-6-v2)
│       ├── scoring_service.py        # Weighted hybrid scoring + sanity layer
│       ├── analysis_validator.py     # Post-extraction cross-encoder validation
│       ├── evidence_validator.py     # Per-skill section parsing + experience classification
│       ├── confidence_service.py     # Analysis confidence formula + level classification
│       ├── improvement_service.py    # Template-based improvement suggestion generation
│       ├── recruiter_service.py      # Recruiter decision matrix + risk level
│       ├── ai_explanation.py         # Gemini narrative explanation generation
│       ├── document_analyzer.py      # Document section structure utilities
│       └── report_service.py         # ReportLab PDF report assembly
└── tests/
    ├── conftest.py
    ├── test_api.py
    ├── test_scoring_service.py
    ├── test_skill_extractor.py
    ├── test_resume_parser.py
    └── test_reliability_optimization.py
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| `api/` | HTTP routing, request validation (FastAPI/Pydantic), response assembly, pipeline timing |
| `services/` | All business logic and AI operations. Single-responsibility per file. |
| `schemas/` | Pydantic v2 models for HTTP request/response bodies and internal service DTOs |
| `core/` | Cross-cutting infrastructure: logging, caching, constants, custom exceptions |
| `config/` | Centralised application settings. All configuration read from environment variables via `pydantic-settings`. |

---

## AI Pipeline

Every `POST /api/analyze` request runs the following sequential pipeline:

```
Step 1  PDF Upload & Validation
        ├── File size check against MAX_PDF_SIZE_MB
        └── PyMuPDF text extraction

Step 2  Skill Extraction + Embedding Generation (concurrent)
        ├── skill_extractor.py
        │   ├── Check SQLite cache (keyed by content hash + model + prompt version)
        │   ├── Primary: Gemini 2.5 Flash Lite structured extraction
        │   │   → matched_skills (with evidence), missing_skills (with importance)
        │   │   → project_experience, candidate_level, strengths, weaknesses
        │   │   → explanation, hiring_recommendation
        │   └── Fallback: local_skill_extractor.py (keyword + regex, no API)
        │
        └── embedding_service.py (asyncio.gather — runs in parallel)
            ├── Primary: Gemini Embedding API (gemini-embedding-001)
            └── Fallback: BGE-base-en-v1.5 (local SentenceTransformer)
            → embeddings for skills section, projects section, experience section

Step 3  Scoring
        └── scoring_service.py
            ├── skill_overlap_score  = earned_points / possible_points × 100
            │   (Exact=1.0, Equivalent=0.9, Partial=0.7, Missing=0.0)
            ├── semantic_similarity_score = composite cosine (calibrated 0–100 scale)
            ├── project_experience_score
            ├── bonus_score
            ├── final_score = skill_score × 0.60 + semantic × 0.40
            └── Sanity layer (upward correction for strong-positive edge cases)

Step 4  Analysis Validation
        └── analysis_validator.py
            Cross-encoder (ms-marco-MiniLM-L-6-v2) re-scores borderline matches
            and may adjust confidence values without changing the structured result.

Step 5  Evidence Validation (per matched skill)
        └── evidence_validator.py
            ├── Section-aware regex parser (experience / projects / skills)
            ├── Action-verb heuristics
            │   (deployed/launched/shipped → Production, built/implemented → Project)
            └── Cross-encoder similarity to resume evidence text
            → experience_level: "Production Experience" | "Project Experience" | "Mention Only"
            → confidence: 0.95 | 0.80 | 0.50

Step 6  Confidence Computation
        └── confidence_service.py
            confidence = verified_ratio × 0.40
                       + semantic_confidence × 0.30
                       + evidence_quality × 0.30
            → confidence_score (0–100), level (HIGH / MEDIUM / LOW), reasons[]

Step 7  Improvement Plan Generation
        └── improvement_service.py
            Template library (30+ skills) → per-missing-skill copy-ready resume snippets
            Ordered: CRITICAL → IMPORTANT → OPTIONAL

Step 8  Recruiter Decision
        └── recruiter_service.py
            Decision matrix:
              score ≥ 85 AND critical_gaps ≤ 2  → Strong Interview Candidate  (Low risk)
              score ≥ 85 AND critical_gaps > 2   → Potential Candidate         (Medium risk)
              score ≥ 70 AND critical_gaps ≤ 2   → Potential Candidate         (Medium risk)
              score ≥ 70 AND critical_gaps > 2   → Potential Candidate         (High risk)
              score < 70                          → Needs Development           (High risk)
            → decision, risk_level, reasons[], candidate_level

Step 9  AI Explanation
        └── ai_explanation.py
            ├── If explanation already returned by Gemini in Step 2 → reuse (no extra API call)
            └── Otherwise: Gemini 2.5 Flash → narrative paragraph
            Result cached in SQLite.

Step 10 Impact Score Injection
        routes.py injects impact_score into each MissingSkill:
          CRITICAL  → −25
          IMPORTANT → −10
          OPTIONAL  →  −5

Step 11 Response Assembly
        AnalyzeResponse assembled and returned as JSON.

Step 12 PDF Report (on demand)
        POST /api/report/download
        └── report_service.py
            ReportLab builds and streams PDF containing all analysis sections.
```

---

## Service Reference

| Service File | Primary Function | Model / Library |
|---|---|---|
| `resume_parser.py` | `extract_text_from_pdf(bytes)` | PyMuPDF |
| `skill_extractor.py` | `extract_skills(resume_text, jd_text)` | Gemini 2.5 Flash Lite + SQLite cache |
| `local_skill_extractor.py` | `extract_skills_local(resume_text, jd_text)` | Keyword/regex (no external API) |
| `embedding_service.py` | `get_similarity(resume_text, jd_text)` | Gemini Embedding API / BGE-base-en-v1.5 |
| `reranker_service.py` | `validate_match(skill, evidence, context)` | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| `scoring_service.py` | `calculate_score(matched, gaps, semantic, ...)` | Deterministic formula |
| `analysis_validator.py` | `validate_and_refine_analysis(result, resume_text)` | Cross-encoder (via reranker_service) |
| `evidence_validator.py` | `validate_skills(matched_skills, resume_text)` | Regex + cross-encoder |
| `confidence_service.py` | `compute_confidence(matched, semantic_score, ...)` | Deterministic formula |
| `improvement_service.py` | `generate_improvements(missing, matched, projects)` | Template library |
| `recruiter_service.py` | `make_decision(score, matched, missing, ...)` | Deterministic decision matrix |
| `ai_explanation.py` | `generate_explanation(...)` | Gemini 2.5 Flash + SQLite cache |
| `document_analyzer.py` | Section parsing utilities | Regex |
| `report_service.py` | `generate_analysis_report(data)` | ReportLab |

---

## API Endpoints

### `POST /api/analyze`

Run the full AI analysis pipeline on a resume and job description.

**Request** — `multipart/form-data`

| Field | Type | Constraints | Description |
|---|---|---|---|
| `resume` | `UploadFile` (PDF) | Required, max `MAX_PDF_SIZE_MB` | Candidate resume file |
| `jd_text` | `string` | Required, min 50 characters | Job description plain text |

**Response** — `200 OK` — `application/json` — `AnalyzeResponse`

```jsonc
{
  "match_score": 84,
  "fallback_mode": false,
  "skill_overlap_score": 77.1,
  "semantic_similarity_score": 84.7,
  "project_experience_score": 65.0,
  "bonus_score": 50.0,
  "skill_semantic_score": 82.0,
  "project_semantic_score": 71.0,
  "experience_semantic_score": 78.0,
  "final_semantic_score": 84.7,
  "hiring_recommendation": "Potential Match",
  "explanation": "The candidate demonstrates strong proficiency in...",
  "strengths": ["Strong Python background", "Production FastAPI experience"],
  "weaknesses": ["No Kubernetes evidence found"],
  "candidate_level": { ... },
  "matched_skills": [
    {
      "skill": "FastAPI",
      "category": "Backend Development",
      "match_type": "EXACT_MATCH",
      "evidence": "Built FastAPI REST APIs deployed on Render...",
      "experience_level": "Production Experience",
      "confidence": 0.95,
      "importance": "CRITICAL"
    }
  ],
  "missing_skills": [
    {
      "skill": "Kubernetes",
      "importance": "CRITICAL",
      "note": "Not found in resume",
      "impact_score": -25,
      "suggestion": "Orchestrated microservices using Kubernetes..."
    }
  ],
  "critical_gaps": [ ... ],
  "recommended_improvements": [ ... ],
  "optional_skills": [ ... ],
  "project_experience": [ ... ],
  "unverified_skills": [ ... ],
  "confidence_analysis": {
    "confidence_score": 82,
    "level": "MEDIUM",
    "reasons": ["Strong production evidence", "Moderate semantic alignment"]
  },
  "recruiter_decision": {
    "decision": "Potential Candidate",
    "risk_level": "Medium",
    "reasons": ["Matched 2 critical requirements", "One critical gap: Kubernetes"],
    "candidate_level": "Mid-level Engineer"
  },
  "improvement_plan": [
    {
      "missing_skill": "Kubernetes",
      "suggestion": "Orchestrated microservices using Kubernetes (Deployments, Services, ConfigMaps)...",
      "priority": "CRITICAL"
    }
  ],
  "score_breakdown": { ... }
}
```

**Error Responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | PDF exceeds `MAX_PDF_SIZE_MB` |
| `422 Unprocessable Entity` | `jd_text` missing or shorter than 50 characters |
| `500 Internal Server Error` | Unexpected pipeline failure |

---

### `POST /api/report/download`

Generate and download a PDF report from an existing analysis payload.

**Request** — `application/json`

The complete `AnalyzeResponse` JSON body as returned by `/api/analyze`.

**Response** — `200 OK` — `application/pdf`

Streamed PDF file.
`Content-Disposition: attachment; filename="AI_Recruiter_Report.pdf"`

---

### `GET /health`

Service health check.

**Response** — `200 OK`

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Pydantic Schema Reference

Key models defined in `app/schemas/analysis.py`:

| Model | Purpose |
|---|---|
| `MatchedSkill` | One matched skill — name, category, match_type, evidence, experience_level, confidence, importance |
| `MissingSkill` | One missing skill — name, importance, note, impact_score, suggestion |
| `SkillEvidence` | Detailed evidence record per skill with verification flag |
| `ProjectExperience` | Detected project pattern — experience label, evidence, detected flag |
| `ConfidenceAnalysis` | confidence_score (0–100), level (HIGH/MEDIUM/LOW), reasons[] |
| `RecruiterDecision` | decision string, risk_level, reasons[], candidate_level |
| `ImprovementSuggestion` | missing_skill, suggestion text, priority |
| `ScoreBreakdown` | Component scores with labels |
| `ScoringResult` | Internal DTO — all scoring outputs before assembly |
| `AnalyzeResponse` | Complete API response model |

---

## Environment Variables

Copy `.env.example` to `.env` and populate values before starting the server.

```bash
cp .env.example .env
```

| Variable | Default | Required | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | `""` | **Yes** | Google AI API key for Gemini models |
| `GEMINI_MODEL` | `gemini-2.0-flash` | No | Legacy fallback model identifier |
| `GEMINI_EXTRACTION_MODEL` | `gemini-2.5-flash-lite` | No | Model used for skill extraction |
| `GEMINI_EXPLANATION_MODEL` | `gemini-2.5-flash` | No | Model used for narrative explanation |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | No | Gemini embedding model name |
| `EMBEDDING_PROVIDER` | `local` | No | `local` uses BGE; `gemini` uses Gemini Embedding API |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | No | Local SentenceTransformer model (auto-downloaded) |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | No | Cross-encoder model for evidence reranking |
| `SKILL_WEIGHT` | `0.60` | No | Skill overlap weight in final score (must sum to 1.0 with `SEMANTIC_WEIGHT`) |
| `SEMANTIC_WEIGHT` | `0.40` | No | Semantic similarity weight in final score |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | No | JSON array of allowed frontend origins |
| `LOG_LEVEL` | `INFO` | No | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_PDF_SIZE_MB` | `10` | No | Maximum accepted PDF upload size in megabytes |
| `GEMINI_RESUME_TOKEN_LIMIT` | `6000` | No | Max resume tokens sent to Gemini extraction |
| `GEMINI_JD_TOKEN_LIMIT` | `3000` | No | Max JD tokens sent to Gemini extraction |

Get a Gemini API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (free tier available).

---

## Setup and Running

### 1. Create and activate a virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **First run:** `sentence-transformers` will download `BAAI/bge-base-en-v1.5` (~440 MB) and `cross-encoder/ms-marco-MiniLM-L-6-v2` (~80 MB) automatically. Ensure internet access during initial startup.

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set GEMINI_API_KEY at minimum
```

### 4. Run development server

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|---|---|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | Swagger UI (interactive API docs) |
| `http://localhost:8000/redoc` | ReDoc documentation |
| `http://localhost:8000/health` | Health check |

### 5. Run in production mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

> Use `--workers 1` if you intend to share the SentenceTransformer model in memory (singleton is process-scoped).

---

## Testing

Tests are located in `tests/` and use `pytest` with `pytest-asyncio`.

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run a specific test module
pytest tests/test_scoring_service.py -v

# Run with stdout (no capture)
pytest tests/ -s

# Run with coverage report (requires pytest-cov)
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

| Test Module | Coverage Area |
|---|---|
| `test_api.py` | End-to-end API endpoint integration (via httpx TestClient) |
| `test_scoring_service.py` | Scoring formula correctness, weight application, sanity layer edge cases |
| `test_skill_extractor.py` | Skill extraction logic, cache behaviour, local fallback activation |
| `test_resume_parser.py` | PDF text extraction, file size validation |
| `test_reliability_optimization.py` | Cache hit/miss, concurrency, fallback reliability |

**Current test count:** 38 passing tests.

---

## Error Handling

The application uses a three-layer error handling strategy:

### Layer 1 — Request Validation (Pydantic)

All incoming requests are validated by Pydantic v2 at the FastAPI boundary. Type mismatches, missing required fields, and constraint violations (e.g. `jd_text` shorter than 50 characters) return `422 Unprocessable Entity` with structured field-level error details automatically.

### Layer 2 — Application Exceptions

| Exception | Source | HTTP Status | Description |
|---|---|---|---|
| `FileSizeLimitError` | `resume_parser.py` | `400` | PDF exceeds `MAX_PDF_SIZE_MB` |
| Gemini `429 / 403` | `skill_extractor.py` | — | Caught internally; fallback pipeline activates; `fallback_mode: true` in response |
| Any service error | All services | — | Logged with full context; propagated to global handler |

### Layer 3 — Global Exception Handler

Registered in `main.py` via `@app.exception_handler(Exception)`. Catches all unhandled exceptions and returns:

```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred."
}
```

Full stack trace is written to structured JSON logs.

### Logging

All services use `get_logger(__name__)` from `app.core.logging`. Logs are emitted as structured JSON with `name`, `levelname`, `message`, and any `extra` fields passed at the call site. Log level is configurable via the `LOG_LEVEL` environment variable.

---

## Performance Optimisations

| Optimisation | Implementation Detail |
|---|---|
| **Model pre-warming** | `EmbeddingService.warmup()` is called during FastAPI `lifespan` startup. The `BAAI/bge-base-en-v1.5` model is loaded into memory before the first request arrives, eliminating cold-start latency. |
| **SentenceTransformer singleton** | Both the embedding model and cross-encoder are stored as class-level attributes (`_model`). Models are loaded once per process and reused across all requests. |
| **Settings singleton** | `get_settings()` uses `@lru_cache`. The `Settings` object is parsed from environment variables exactly once per process lifetime. |
| **Parallel extraction + embedding** | `asyncio.gather(extract_skills(...), get_similarity(...))` in `routes.py` runs skill extraction and embedding generation concurrently, reducing end-to-end latency. |
| **SQLite response cache** | Gemini extraction results are cached in `.cache/gemini_cache.db` keyed by `sha256(resume_text + jd_text) + model_name + prompt_version`. Explanation results are cached separately. Cache entries can carry a TTL (e.g. local fallback results expire after 15 minutes). Identical requests return instantly with zero API quota consumed. |
| **Token limiting** | Resume and JD texts are truncated to `GEMINI_RESUME_TOKEN_LIMIT` / `GEMINI_JD_TOKEN_LIMIT` before being sent to the Gemini API, controlling cost and latency. |
| **Async endpoints** | All route handlers are `async def`. Blocking model inference operations (SentenceTransformer encode, cross-encoder predict) are wrapped in `asyncio.to_thread()` to avoid blocking the event loop. |
| **No-hallucination policy** | `evidence_validator.py` uses only local computation (regex + cross-encoder). No additional Gemini API calls are made after the initial extraction step. |
