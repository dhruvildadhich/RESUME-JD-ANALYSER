# Frontend Application

React-based analysis dashboard for the Resume–JD Matcher platform. Provides resume and job description upload, a real-time AI processing progress view, and a structured recruiter intelligence dashboard displaying match scores, skill analysis, gap assessment, and improvement recommendations.

---

## Table of Contents

- [Requirements](#requirements)
- [Features](#features)
- [Architecture](#architecture)
- [Component Reference](#component-reference)
- [API Communication](#api-communication)
- [Setup and Running](#setup-and-running)
- [UI Design Principles](#ui-design-principles)

---

## Requirements

| Dependency | Version | Purpose |
|---|---|---|
| Node.js | 18+ | Runtime |
| React | 19.x | UI framework |
| Vite | 8.x | Build tool and HMR dev server |
| Tailwind CSS | 3.x | Utility-first CSS |
| Framer Motion | 12.x | Animation library |
| Axios | 1.x | HTTP client |
| Lucide React | 1.x | Icon library |
| TypeScript | 6.x | Type checking (via `tsc`) |

---

## Features

| Feature | Component |
|---|---|
| PDF resume upload with file type and size validation | `UploadForm.jsx` |
| Job description text input | `UploadForm.jsx` |
| PDF resume preview panel with section highlighting | `ResumePreview.jsx`, `HighlightedText.jsx` |
| JD preview with matched/missing keyword highlighting | `JDPreview.jsx` |
| AI analysis step progress animation (5 stages) | `AIAnalysisProgress.jsx` |
| Error boundary to prevent full-page crashes | `AnalysisErrorBoundary` (in `AIAnalysisProgress.jsx`) |
| Recruiter decision card (verdict + risk + reasons) | `RecruiterDecisionCard.jsx` |
| Overall match score with animated circular gauge | `ScoreCard.jsx`, `ScoreGauge.jsx` |
| Confidence analysis with SVG ring progress | `ConfidenceCard.jsx` |
| Matched skills accordion (expand per-skill evidence) | `MatchedSkills.jsx`, `AccordionCard.jsx` |
| Missing skills accordion (expand reason + suggestion) | `MissingSkills.jsx`, `AccordionCard.jsx` |
| AI explanation narrative with strengths/weaknesses | `ExplanationCard.jsx` |
| Improvement roadmap with copy-to-clipboard snippets | `ImprovementPlan.jsx` |
| PDF report download (streamed from backend) | `App.jsx` + `api.js` |
| Fallback mode banner when AI service is degraded | `AnalysisDashboard.jsx` |

---

## Architecture

```
frontend/
├── src/
│   ├── App.jsx                     # Root application, state machine, layout
│   ├── main.jsx                    # React entry point
│   ├── index.css                   # Global styles, scrollbar, keyframe animations
│   │
│   ├── components/
│   │   ├── UploadForm.jsx          # Resume + JD input form
│   │   ├── LoadingSpinner.jsx      # Inline loading indicator
│   │   ├── ScoreGauge.jsx          # Animated circular score dial
│   │   │
│   │   ├── analysis/               # Result dashboard components
│   │   │   ├── AnalysisDashboard.jsx      # Orchestrates result layout
│   │   │   ├── AIAnalysisProgress.jsx     # 5-step loading timeline
│   │   │   ├── ScoreCard.jsx              # Overall score + component bars
│   │   │   ├── RecruiterDecisionCard.jsx  # Hire decision verdict
│   │   │   ├── ConfidenceCard.jsx         # SVG ring + confidence reasons
│   │   │   ├── MatchedSkills.jsx          # Accordion matched skill cards
│   │   │   ├── MissingSkills.jsx          # Accordion missing skill cards
│   │   │   ├── ExplanationCard.jsx        # Score bars + AI narrative
│   │   │   ├── ImprovementPlan.jsx        # Skill improvement snippets
│   │   │   └── SuggestionsList.jsx        # Generic suggestion list
│   │   │
│   │   ├── preview/                # Document preview components
│   │   │   ├── ResumePreview.jsx          # Resume text preview panel
│   │   │   ├── JDPreview.jsx              # JD preview with skill highlights
│   │   │   ├── HighlightedText.jsx        # Keyword span highlighter
│   │   │   └── PreviewModal.jsx           # Full-screen preview modal
│   │   │
│   │   └── ui/                     # Primitive design system components
│   │       ├── index.js                   # Barrel export
│   │       ├── AccordionCard.jsx          # Reusable expand/collapse card
│   │       ├── Badge.jsx                  # Match type / importance badges
│   │       ├── Button.jsx                 # Primary / secondary button
│   │       ├── Card.jsx                   # Surface card container
│   │       ├── Input.jsx                  # Text input primitive
│   │       ├── LoadingState.jsx           # Skeleton loading state
│   │       └── MetricCard.jsx             # Numeric metric display card
│   │
│   ├── services/
│   │   └── api.js                  # Axios instance + analyzeResume(), downloadReport()
│   │
│   └── styles/
│       └── designTokens.js         # COLORS, TYPOGRAPHY, SPACING, RADIUS, SHADOWS
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

---

## Component Reference

### Application Shell

#### `App.jsx`

Root component. Manages a three-state state machine:

| State | Description |
|---|---|
| `IDLE` | Initial upload form shown |
| `LOADING` | Analysis in progress — document previews + `AIAnalysisProgress` |
| `RESULTS` | Full dashboard — document previews + `AnalysisDashboard` |

Handles: form submission, API call, error state, report download, and reset.

---

### Analysis Components (`components/analysis/`)

#### `AnalysisDashboard.jsx`
Top-level result orchestrator. Renders components in this order: RecruiterDecisionCard → ScoreCard → ConfidenceCard → MatchedSkills + MissingSkills → ExplanationCard → ImprovementPlan.

#### `AIAnalysisProgress.jsx`
Five-step animated progress timeline displayed while the backend processes the request. Steps advance on fixed timers and complete instantly when the API responds. Includes `AnalysisErrorBoundary` (class component) that catches render errors and shows a retry button instead of crashing the page.

#### `RecruiterDecisionCard.jsx`
Displays the top-level recruiter verdict (`Strong Interview Candidate` / `Potential Candidate` / `Needs Development`), risk level badge, candidate level label, and a 3-point reasoning list. Colour-coded by decision outcome.

#### `ConfidenceCard.jsx`
Animated SVG circular progress ring showing the analysis confidence score (0–100) with `HIGH` / `MEDIUM` / `LOW` level label and a list of reasons contributing positively or negatively to confidence.

#### `MatchedSkills.jsx`
Scrollable list of matched skills using `AccordionCard`. Collapsed row shows: skill name, match type badge (Exact/Equivalent/Partial), experience level (★ stars), category, and confidence percentage. Expanded row shows the full resume evidence sentence.

#### `MissingSkills.jsx`
Scrollable list of missing skills grouped by severity (Critical Gaps / Recommended / Optional). Each row uses `AccordionCard`. Collapsed row shows: skill name, impact score badge, importance badge. Expanded row shows the reason note and improvement suggestion.

#### `ExplanationCard.jsx`
Two sub-sections: (1) Score breakdown — `Skill Alignment` and `Experience Relevance` progress bars without internal weighting formulas. (2) Explanation — hiring recommendation badge, AI narrative paragraph, and two-column Strengths / Areas to Improve lists.

#### `ImprovementPlan.jsx`
Grouped by priority (Critical → Recommended → Optional). Each item shows the missing skill name, full improvement snippet, and a copy-to-clipboard button that turns green with a checkmark on copy.

#### `ScoreCard.jsx`
Displays the overall match score using `ScoreGauge` (animated circular dial) alongside component scores and a seniority level indicator.

---

### Preview Components (`components/preview/`)

#### `ResumePreview.jsx`
Renders extracted resume text in a readable panel format.

#### `JDPreview.jsx`
Renders the job description text. Matched and missing skill keywords are highlighted using `HighlightedText.jsx`.

#### `HighlightedText.jsx`
Splits a text string and wraps skill keywords in styled `<mark>` spans with colour differentiation for matched vs missing skills.

---

### UI Primitives (`components/ui/`)

#### `AccordionCard.jsx`
Reusable expand/collapse card. Summary row always visible; detail body expands with a CSS `max-height` transition. Accepts `accentColor`, `summary` (JSX), and `children` (JSX for expanded body). Chevron rotates 180° on open. Click is captured on the outer wrapper; inner content uses `stopPropagation`.

#### `Badge.jsx`
Renders styled pill badges for match types (`exact`, `equivalent`, `partial`) and importance levels (`critical`, `recommended`, `optional`).

#### `Card.jsx`
Surface container with consistent border, background, and padding from the design token system.

#### `Button.jsx`
`primary` and `secondary` variants with hover state and disabled styling.

---

### Services (`services/`)

#### `api.js`

```js
// Axios instance — 2 min timeout for backend AI processing
const client = axios.create({ baseURL: "http://localhost:8000", timeout: 120000 });

analyzeResume(formData)     // POST /api/analyze — multipart/form-data
downloadReport(payload)     // POST /api/report/download — JSON
```

---

### Design Tokens (`styles/designTokens.js`)

All colours, spacing, typography, radius, and shadow values are centralised here. Components reference these tokens via imported constants rather than hardcoded values.

| Export | Contents |
|---|---|
| `COLORS` | `ink`, `ink-muted`, `canvas`, `surface-1/2`, `hairline`, `accent-blue`, `gradient-*`, `semantic.*` |
| `TYPOGRAPHY` | `fontFamily.display/body`, scale objects (`bodySM`, `caption`, `micro`, `headline`, etc.) |
| `SPACING` | `xxs` (4px) → `section` (96px) |
| `RADIUS` | `xs` (4px) → `pill` (100px) |
| `SHADOWS` | `none`, `surface`, `floating`, `selected` |

---

## API Communication

The frontend communicates exclusively with the FastAPI backend over HTTP.

```
User Action           Frontend               Backend
─────────────         ────────               ───────
Submit form    ──▶    analyzeResume()  ──▶   POST /api/analyze
                      axios.post()           (multipart/form-data)
                                      ◀──   AnalyzeResponse JSON
               ◀──    results state
               
Download click ──▶    downloadReport() ──▶  POST /api/report/download
                      axios.post()           (JSON body)
                      responseType: blob    ◀──   PDF stream
               ◀──    browser download trigger
```

The Axios timeout is set to 120 seconds to accommodate the full AI pipeline (PDF parsing + Gemini extraction + embedding + scoring + explanation).

Errors are caught at the `analyzeResume()` call site in `App.jsx` and surfaced in `AIAnalysisProgress` via the `isError` + `errorMessage` props.

---

## Setup and Running

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start the development server

```bash
npm run dev
```

Application available at `http://localhost:5173`.

> Ensure the backend is running at `http://localhost:8000` before submitting an analysis.

### 3. Build for production

```bash
npm run build
```

Output is written to `dist/`. Serve with any static file host or reverse proxy.

### 4. Preview the production build locally

```bash
npm run preview
```

---

## UI Design Principles

| Principle | Implementation |
|---|---|
| **Dark glass aesthetic** | `canvas: #090909` background, `surface-1: #141414` cards, semi-transparent borders |
| **Design token system** | All visual values centralised in `designTokens.js`; no hardcoded hex values in components |
| **Progressive disclosure** | `AccordionCard` keeps skill lists compact by default; evidence and suggestions expand on demand |
| **Recruiter-focused language** | No internal technical terminology exposed in the UI (no model names, no formula weights) |
| **Loading states** | `AIAnalysisProgress` provides 5-step timeline animation; `Skeleton` components prevent layout shift |
| **Responsive layout** | Two-column grids collapse to single column on small screens via Tailwind responsive breakpoints |
| **Error resilience** | `AnalysisErrorBoundary` prevents individual component crashes from destroying the entire dashboard |
| **Smooth animations** | Framer Motion for accordion transitions; CSS `transition` for progress bars and hover states |
