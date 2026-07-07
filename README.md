# Resume–JD AI Matcher

An AI-powered recruitment intelligence platform that evaluates a candidate's resume against a job description. The system extracts skills using an LLM, measures semantic alignment using dense embeddings, classifies evidence depth per skill, and produces a structured recruiter-quality evaluation — including a match score, gap analysis, recruiter decision, confidence rating, and a personalised improvement roadmap.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [AI System Architecture](#ai-system-architecture)
- [Tech Stack](#tech-stack)
- [Scoring Methodology](#scoring-methodology)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Output Overview](#output-overview)
- [Contributing](#contributing)

---

## Problem Statement

Traditional resume screening is slow, inconsistent, and subjective. Recruiters spend significant time manually comparing resumes against job descriptions with no standardised way to measure alignment, validate experience depth, or generate actionable feedback.

This platform automates that process:

- Parses a candidate PDF resume and extracts structured information (skills, projects, experience).
- Parses the job description to identify required and preferred skills with importance classification.
- Uses LLM-based extraction with embedding-based semantic comparison to produce an objective, evidence-grounded match score.
- Identifies matched skills with resume evidence, classifies missing skills by impact, and generates per-skill improvement suggestions.
- Produces a recruiter-readable decision (Strong / Potential / Needs Development) with supporting reasons.

---

## Key Features

| Feature | Description |
|---|---|
| **Resume PDF Parsing** | Extracts raw text from uploaded PDF using PyMuPDF |
| **LLM Skill Extraction** | Gemini 2.5 Flash Lite extracts matched skills, missing skills, projects, seniority level, and hiring recommendation |
| **Local Fallback Extraction** | Keyword + regex NLP pipeline activates automatically when the Gemini API is unavailable |
| **Evidence Extraction** | Every matched skill is linked to a specific sentence from the resume as verification proof |
| **Experience Depth Classification** | Each skill classified as Production Experience (95%), Project Experience (80%), or Mention Only (50%) using cross-encoder + section heuristics |
| **Semantic Embedding** | `BAAI/bge-base-en-v1.5` local embeddings compute cosine similarity across resume sections |
| **Gemini Embeddings** | Gemini Embedding API (`gemini-embedding-001`) used as the primary embedding source when available |
| **Hybrid Scoring Engine** | Weighted combination of skill overlap score (60%) and semantic similarity score (40%) |
| **Match Type Classification** | Exact (1.0), Equivalent (0.9), Partial (0.7) per-skill point weights |
| **Sanity Validation Layer** | Score adjustment for strong-positive edge cases to prevent undervaluing broad-coverage candidates |
| **Missing Skill Impact Scoring** | Gaps classified as Critical (−25), Important (−10), Optional (−5) |
| **Analysis Confidence Score** | Evidence-weighted reliability rating with HIGH / MEDIUM / LOW level and reasons |
| **Recruiter Decision Engine** | Deterministic verdict with risk level and supporting evidence from matched/missing skills |
| **Improvement Roadmap** | 30+ skill-specific copy-ready resume snippets, ordered by priority |
| **AI Explanation** | Narrative evaluation with strengths, weaknesses, and hiring recommendation |
| **PDF Report Export** | Downloadable professional PDF report via ReportLab |
| **SQLite Response Cache** | Gemini extraction and explanation responses cached locally by content hash to eliminate redundant API calls |
| **Model Pre-warming** | Embedding model loaded into memory at startup via FastAPI lifespan — no cold start on first request |
| **Interactive Dashboard** | React frontend with accordion skill cards, animated confidence ring, recruiter decision card, and improvement plan |

---

## AI System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                           User Input                               │
│              Resume PDF   +   Job Description Text                 │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
                      ┌──────────────────┐
                      │  Resume Parser   │  PyMuPDF — raw text extraction
                      └────────┬─────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │    Skill Extractor     │  Primary: Gemini 2.5 Flash Lite
                  │                        │  → matched skills + evidence
                  │    Local Fallback      │  → missing skills + importance
                  │    (Keyword / Regex)   │  → project experience
                  └────────────┬───────────┘  → seniority level
                               │
              ┌────────────────┴────────────────┐
              │  (concurrent via asyncio.gather) │
              ▼                                  ▼
  ┌───────────────────────┐         ┌────────────────────────────┐
  │   Embedding Service   │         │     Analysis Validator     │
  │                       │         │                            │
  │  Primary:             │         │  Cross-encoder reranking   │
  │  Gemini Embedding API │         │  (ms-marco-MiniLM-L-6-v2) │
  │                       │         │  Validates borderline      │
  │  Fallback:            │         │  skill matches             │
  │  BGE-base-en-v1.5     │         └──────────────┬─────────────┘
  │  (local)              │                        │
  └──────────┬────────────┘                        │
             └──────────────────┬──────────────────┘
                                │
                                ▼
                   ┌────────────────────────┐
                   │    Scoring Service     │
                   │                        │
                   │  skill_score × 0.60   │
                   │  + semantic × 0.40    │
                   │  + sanity layer       │
                   │  → final_score (0–100)│
                   └───────────┬────────────┘
                               │
               ┌───────────────┴────────────────┐
               │                                │
               ▼                                ▼
  ┌──────────────────────┐       ┌──────────────────────────┐
  │  Evidence Validator  │       │   Confidence Service     │
  │                      │       │                          │
  │  Per-skill section   │       │  verified_ratio × 0.40  │
  │  parsing + action    │       │  + semantic_conf × 0.30  │
  │  verb heuristics     │       │  + evidence_qual × 0.30  │
  │  → Production /      │       │  → HIGH / MEDIUM / LOW   │
  │    Project / Mention │       └──────────────┬───────────┘
  └──────────┬───────────┘                      │
             └──────────────────┬───────────────┘
                                │
               ┌────────────────┴──────────────────┐
               │                                   │
               ▼                                   ▼
  ┌──────────────────────┐         ┌───────────────────────────┐
  │  Improvement Service │         │    Recruiter Service      │
  │                      │         │                           │
  │  Template library    │         │  Decision matrix:         │
  │  (30+ skills)        │         │  ≥85 + ≤2 gaps → Strong  │
  │  → priority-ordered  │         │  ≥70           → Potential│
  │    resume snippets   │         │  <70           → Needs    │
  └──────────┬───────────┘         │                Development│
             │                     └──────────────┬────────────┘
             └──────────────────┬─────────────────┘
                                │
                                ▼
                   ┌────────────────────────┐
                   │   AI Explanation       │  Gemini 2.5 Flash
                   │   Generator            │  → narrative summary
                   │                        │  → strengths / weaknesses
                   │   (SQLite cached)      │  → hiring recommendation
                   └───────────┬────────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │     API Response       │  JSON AnalyzeResponse
                   │                        │
                   │     PDF Report         │  ReportLab (on demand)
                   └───────────┬────────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │    React Dashboard     │
                   │                        │
                   │  Recruiter Decision    │
                   │  → Score Overview      │
                   │  → Confidence Ring     │
                   │  → Accordion Skills    │
                   │  → Explanation         │
                   │  → Improvement Plan    │
                   └────────────────────────┘
```

**Why a hybrid approach?**

Pure keyword matching misses synonyms and equivalent technologies (e.g. "Postgres" vs "PostgreSQL", "GCP" vs "Google Cloud"). Pure semantic similarity cannot distinguish "familiar with Docker" from "deployed Kubernetes clusters to production." The hybrid combines:

- **LLM extraction** for structured, context-aware skill identification with evidence
- **Dense embeddings** for meaning-level alignment across resume sections
- **Cross-encoder reranking** for per-skill evidence verification without hallucination
- **Deterministic scoring rules** for reproducibility and auditability

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| React | 19.x | UI framework |
| Vite | 8.x | Build tool and HMR dev server |
| Tailwind CSS | 3.x | Utility-first CSS framework |
| Framer Motion | 12.x | Animation — accordion, transitions |
| Axios | 1.x | HTTP client for API communication |
| Lucide React | 1.x | Icon set |
| TypeScript | 6.x | Type checking (`tsc` in build) |

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Runtime |
| FastAPI | ≥ 0.111.1 | Async REST API framework |
| Uvicorn | ≥ 0.30.1 | ASGI server |
| Pydantic v2 | ≥ 2.7.4 | Request/response schema validation |
| pydantic-settings | ≥ 2.3.4 | Environment-based configuration |
| python-multipart | ≥ 0.0.9 | Multipart file upload parsing |
| python-dotenv | ≥ 1.0.1 | `.env` file loading |
| python-json-logger | ≥ 2.0.7 | Structured JSON logging |

### AI / ML

| Technology | Model / Version | Purpose |
|---|---|---|
| Google Gemini | `gemini-2.5-flash-lite` | Skill extraction from resume and JD |
| Google Gemini | `gemini-2.5-flash` | Narrative explanation generation |
| Google Gemini Embeddings | `gemini-embedding-001` | Primary semantic embeddings |
| SentenceTransformer | `BAAI/bge-base-en-v1.5` | Local embedding fallback + confidence scoring |
| SentenceTransformer | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder reranking and evidence validation |
| PyMuPDF | ≥ 1.28.0 | PDF text extraction |
| ReportLab | ≥ 4.2.0 | PDF report generation |
| NumPy | ≥ 2.0.0 | Vector operations |
| PyTorch | ≥ 2.0.0 | SentenceTransformer runtime |

### Infrastructure

| Tool | Purpose |
|---|---|
| SQLite | Local response cache for Gemini API calls |
| pytest + pytest-asyncio | Backend unit and integration test suite |
| httpx | Async HTTP client for test requests |

---

## Scoring Methodology

The final match score (0–100) is a weighted combination of two independently computed components.

### Component 1 — Skill Match Score (60%)

The LLM identifies all JD-required skills and classifies each against the resume. Point weights per match:

| Match Type | Weight | Description |
|---|---|---|
| Exact | 1.00 | Identical or near-identical skill name |
| Equivalent | 0.90 | Different name, same capability (e.g. Postgres ↔ PostgreSQL) |
| Partial | 0.70 | Related technology or a subset of the required skill |
| Missing | 0.00 | Not found in the resume |

`skill_score = (sum of earned points / sum of possible points) × 100`

### Component 2 — Semantic Similarity Score (40%)

Cosine similarity is computed between dense embeddings of the resume (skills, projects, experience sections) and the JD. Scores are mapped to a 0–100 scale using calibrated thresholds:

| Cosine Range | Interpretation |
|---|---|
| ≥ 0.75 | Excellent semantic alignment |
| 0.65 – 0.75 | Strong alignment |
| 0.50 – 0.65 | Moderate alignment |
| < 0.50 | Weak alignment |

### Final Score

```
final_score = (skill_score × 0.60) + (semantic_score × 0.40)
```

A sanity validation layer applies upward corrections when strong positive signals are detected (e.g. ≥30 matched skills, ≤2 critical gaps) to prevent the formula from systematically undervaluing candidates with extensive but broad skill coverage.

---

## Project Structure

```
resume-jd-matcher/
│
├── backend/                      # FastAPI AI analysis engine
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # POST /api/analyze, POST /api/report/download
│   │   ├── config/
│   │   │   └── settings.py       # pydantic-settings — all env vars
│   │   ├── core/
│   │   │   ├── cache.py          # SQLite response cache (extraction + explanation)
│   │   │   ├── constants.py      # Match types, importance levels, scoring thresholds
│   │   │   ├── exceptions.py     # FileSizeLimitError and custom exception classes
│   │   │   ├── logging.py        # Structured JSON logging configuration
│   │   │   └── skill_ontology.py # Skill synonym and equivalence mappings
│   │   ├── schemas/
│   │   │   └── analysis.py       # All Pydantic models (AnalyzeResponse, MatchedSkill, etc.)
│   │   └── services/             # AI pipeline — one responsibility per file
│   │       ├── resume_parser.py
│   │       ├── skill_extractor.py
│   │       ├── local_skill_extractor.py
│   │       ├── embedding_service.py
│   │       ├── scoring_service.py
│   │       ├── analysis_validator.py
│   │       ├── evidence_validator.py
│   │       ├── confidence_service.py
│   │       ├── improvement_service.py
│   │       ├── recruiter_service.py
│   │       ├── ai_explanation.py
│   │       ├── reranker_service.py
│   │       ├── document_analyzer.py
│   │       └── report_service.py
│   ├── tests/                    # pytest test suite (38 tests)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                     # React analysis dashboard
│   ├── src/
│   │   ├── App.jsx               # Root — 3-state machine (IDLE / LOADING / RESULTS)
│   │   ├── components/
│   │   │   ├── analysis/         # Dashboard result components
│   │   │   ├── preview/          # Resume and JD preview panels
│   │   │   └── ui/               # Design system primitives (Card, Badge, AccordionCard…)
│   │   ├── services/
│   │   │   └── api.js            # Axios client — analyzeResume(), downloadReport()
│   │   └── styles/
│   │       └── designTokens.js   # COLORS, TYPOGRAPHY, SPACING, RADIUS, SHADOWS
│   ├── package.json
│   └── vite.config.ts
│
├── README.md                     # This file
├── backend/README.md             # Backend service documentation
└── frontend/README.md            # Frontend application documentation
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.12 recommended |
| Node.js | 18+ | LTS recommended |
| Google Gemini API key | — | [Get one free at Google AI Studio](https://aistudio.google.com/app/apikey) |
| ~4 GB disk space | — | For PyTorch + SentenceTransformer model downloads |
| Internet access (first run) | — | Models auto-downloaded on startup |

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd resume-jd-matcher
```

**Terminal 1 — Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Open .env and set: GEMINI_API_KEY=<your-key>

uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Terminal 2 — Frontend**

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

> The SentenceTransformer models (`BAAI/bge-base-en-v1.5` and `cross-encoder/ms-marco-MiniLM-L-6-v2`) are downloaded automatically on first startup. This requires an internet connection and may take a few minutes.

For complete setup details, environment variable reference, and production deployment notes, see:

- [`backend/README.md`](./backend/README.md)
- [`frontend/README.md`](./frontend/README.md)

---

## Output Overview

After a resume and job description are submitted, the analysis dashboard displays the following sections in order:

| Section | Content |
|---|---|
| **Recruiter Decision** | Top-level verdict (Strong Interview Candidate / Potential Candidate / Needs Development), risk level (Low / Medium / High), candidate level label, and 3-point supporting reasons |
| **Match Score** | Overall 0–100 score (animated dial), Skill Alignment score, Experience Relevance score |
| **Confidence Analysis** | Evidence-weighted reliability score with level badge and contributing reasons |
| **Matched Skills** | Accordion list — collapsed shows skill name, match type, experience depth (★ stars), category, confidence %; expanded shows the evidence sentence from the resume |
| **Missing Skills** | Accordion list grouped by Critical / Recommended / Optional — collapsed shows skill name and impact score; expanded shows the gap reason and improvement suggestion |
| **Explanation** | AI narrative paragraph, hiring recommendation badge, Strengths and Areas to Improve |
| **Improvement Roadmap** | Per-missing-skill, copy-paste-ready resume bullet points, grouped by priority |
| **PDF Report** | One-click download — includes all sections above in a structured PDF |

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes and run tests: `cd backend && pytest tests/ -v`
4. Ensure the frontend builds: `cd frontend && npm run build`
5. Open a pull request with a clear description of the change.
