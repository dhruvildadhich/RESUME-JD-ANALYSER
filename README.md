# Resume–JD Matcher 🎯

> **AI-powered resume analysis** — compare a candidate resume against a job description, extract skills, calculate a hybrid match score, and receive actionable improvement suggestions.

Built as a production-quality AI MVP using **FastAPI**, **Gemini API**, **Sentence Transformers**, and **React + Tailwind CSS**.

---

## ✨ Features

| Feature | Details |
|---|---|
| **PDF Resume Parsing** | Extracts clean text from any standard PDF using PyMuPDF |
| **AI Skill Extraction** | Gemini API extracts and normalises technical skills from both resume and JD |
| **Semantic Similarity** | SentenceTransformer `all-MiniLM-L6-v2` computes dense-vector cosine similarity |
| **Hybrid Match Score** | 60% skill overlap + 40% semantic similarity → integer 0–100 |
| **AI Explanation** | Gemini generates strengths, weaknesses, narrative, and hiring recommendation |
| **Improvement Suggestions** | 5 actionable, personalised resume improvement tips |
| **Dark Dashboard UI** | React + Tailwind glassmorphism dashboard with animated score gauge |

---

## 🏗️ Architecture

```
resume-jd-matcher/
├── backend/
│   └── app/
│       ├── api/            ← FastAPI routes (POST /api/analyze)
│       ├── services/       ← Business logic (parser, extractor, embeddings, scoring, AI)
│       ├── schemas/        ← Pydantic v2 request/response models
│       ├── config/         ← pydantic-settings environment config
│       └── core/           ← Logging + custom exceptions
└── frontend/
    └── src/
        ├── components/     ← UploadForm, ScoreGauge, SkillBadges, ExplanationCard, SuggestionsList
        └── services/       ← Axios API client
```

### Analysis Pipeline

```
PDF Upload
    │
    ▼
[1] Resume Parser    — PyMuPDF → clean text
    │
    ▼
[2] Skill Extractor  — Gemini JSON → resume_skills[], jd_skills[]
    │
    ▼
[3] Embedding Svc    — SentenceTransformer → cosine_similarity
    │
    ▼
[4] Scoring Svc      — 60% skill_overlap + 40% semantic → final_score
    │
    ▼
[5] AI Explanation   — Gemini → strengths, weaknesses, suggestions, recommendation
    │
    ▼
    AnalyzeResponse JSON
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (tested on 3.14; PyMuPDF 1.28.0 ships pre-built wheels for arm64/x86_64)
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier available)

---

### Backend Setup

```bash
# 1. Navigate to backend
cd resume-jd-matcher/backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and set GEMINI_API_KEY=your_key_here

# 5. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000/api/analyze
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

### Frontend Setup

```bash
# 1. Navigate to frontend
cd resume-jd-matcher/frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000 (already set)

# 4. Start dev server
npm run dev
```

Frontend will be at **http://localhost:5173**

---

## 🔌 API Reference

### `POST /api/analyze`

Analyse a resume against a job description.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `resume` | `file` | PDF resume (max 10 MB) |
| `jd_text` | `string` | Job description text (min 50 chars) |

**Response** — `application/json`

```json
{
  "match_score": 74,
  "matched_skills": ["python", "fastapi", "postgresql"],
  "missing_skills": ["docker", "kubernetes"],
  "strengths": ["Strong Python background", "REST API experience"],
  "weaknesses": ["No containerisation experience", "Missing CI/CD tools"],
  "explanation": "The candidate demonstrates strong backend skills...",
  "suggestions": [
    "Complete Docker Fundamentals certification on Docker.com",
    "Build and deploy a containerised FastAPI project to AWS ECS",
    "..."
  ],
  "hiring_recommendation": "Potential Match",
  "skill_overlap_score": 60.0,
  "semantic_similarity_score": 82.5
}
```

**Error responses**

| Status | Error | Cause |
|---|---|---|
| 413 | `file_too_large` | PDF > 10 MB |
| 422 | `pdf_parse_error` | Corrupt / encrypted / image-only PDF |
| 422 | Validation error | Missing or invalid form fields |
| 502 | `gemini_api_error` | Gemini API unavailable or bad response |
| 500 | `embedding_error` | Embedding model failure |

---

## 🧪 Testing

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
```

Test modules:
- `test_resume_parser.py` — PDF parsing and text cleaning
- `test_skill_extractor.py` — JSON parsing and skill normalisation (Gemini mocked)
- `test_scoring_service.py` — Hybrid scoring edge cases
- `test_api.py` — Integration tests (all external deps mocked)

---

## ⚙️ Configuration

All configuration lives in `.env` (backend) and `.env` (frontend):

### Backend `.env`

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | **Required.** Your Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `SKILL_WEIGHT` | `0.60` | Weight for skill overlap component |
| `SEMANTIC_WEIGHT` | `0.40` | Weight for semantic similarity component |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed frontend origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MAX_PDF_SIZE_MB` | `10` | Maximum PDF upload size |

### Frontend `.env`

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

---

## 🤖 AI Engineering Notes

### Hybrid Scoring Formula
```
final_score = 0.60 × skill_overlap_score + 0.40 × (semantic_similarity × 100)
```
- **Skill overlap** rewards exact skill matches — the most direct measure of JD fit.
- **Semantic similarity** captures broader relevance — experience domain, role context, and soft alignment.
- The 60/40 weighting reflects that ATS systems are primarily keyword-driven.

### Gemini Prompting Strategy
- **Skill extraction**: JSON-only output with strict schema, normalisation rules, and duplicate removal.
- **Explanation**: Role-prompted as "senior technical recruiter" with a structured JSON output schema. Score-thresholded hiring recommendation prevents hallucination.
- Both prompts strip markdown fences from Gemini output to handle inconsistent formatting.

### Embedding Model Choice
`all-MiniLM-L6-v2` was chosen for:
- Fast inference (~80 MB, runs CPU-only)
- Strong performance on semantic textual similarity benchmarks
- No API cost (fully local)
- Pre-normalised dot product = O(1) cosine similarity

---

## 📁 Project Structure

```
resume-jd-matcher/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # POST /api/analyze
│   │   ├── config/
│   │   │   └── settings.py         # pydantic-settings env config
│   │   ├── core/
│   │   │   ├── exceptions.py       # Domain HTTP exceptions
│   │   │   └── logging.py          # Structured JSON logging
│   │   ├── schemas/
│   │   │   └── analysis.py         # Pydantic v2 models
│   │   ├── services/
│   │   │   ├── resume_parser.py    # PyMuPDF text extraction
│   │   │   ├── skill_extractor.py  # Gemini skill extraction
│   │   │   ├── embedding_service.py # SentenceTransformer similarity
│   │   │   ├── scoring_service.py  # Hybrid 60/40 scoring
│   │   │   └── ai_explanation.py  # Gemini explanation generation
│   │   └── main.py                 # FastAPI app factory
│   ├── tests/
│   │   ├── test_resume_parser.py
│   │   ├── test_skill_extractor.py
│   │   ├── test_scoring_service.py
│   │   └── test_api.py
│   ├── .env.example
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── UploadForm.jsx       # Drag-drop PDF upload + JD textarea
│       │   ├── ScoreGauge.jsx       # SVG circular score indicator
│       │   ├── SkillBadges.jsx      # Matched/missing skill chips
│       │   ├── ExplanationCard.jsx  # AI narrative + score bars
│       │   ├── SuggestionsList.jsx  # Improvement suggestions
│       │   └── LoadingSpinner.jsx   # Analysis loading state
│       ├── services/
│       │   └── api.js               # Axios API client
│       ├── App.jsx                  # State machine + layout
│       └── index.css                # Tailwind + custom styles
│
└── README.md
```

---

## 🛡️ Production Considerations

- **Error handling** — domain-specific HTTP exceptions at every layer
- **Input validation** — Pydantic v2 enforces types + constraints on all I/O
- **Token guards** — resume and JD text are truncated before Gemini calls
- **File size limits** — configurable via `MAX_PDF_SIZE_MB`
- **Singleton model** — embedding model loaded once at startup, thread-safe
- **Structured logging** — JSON logs with structured context fields
- **CORS** — configurable allowed origins
- **Health endpoint** — `GET /health` for load-balancer probes

---

## 📄 License

MIT
