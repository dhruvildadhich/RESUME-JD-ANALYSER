import React, { useState } from "react";
import ExplanationCard from "./components/ExplanationCard";
import LoadingSpinner from "./components/LoadingSpinner";
import ScoreGauge from "./components/ScoreGauge";
import SkillBadges from "./components/SkillBadges";
import SuggestionsList from "./components/SuggestionsList";
import UploadForm from "./components/UploadForm";
import { Card, MetricCard, Button, Badge } from "./components/ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "./styles/designTokens";
import { analyzeResume } from "./services/api";

const STATE = {
  IDLE: "idle",
  LOADING: "loading",
  RESULTS: "results",
  ERROR: "error",
};

export default function App() {
  const [appState, setAppState] = useState(STATE.IDLE);
  const [results, setResults] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleAnalyse = async (resumeFile, jdText) => {
    setAppState(STATE.LOADING);
    setErrorMessage("");
    try {
      const data = await analyzeResume(resumeFile, jdText);
      setResults(data);
      setAppState(STATE.RESULTS);
      setTimeout(() => document.getElementById("results-section")?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (err) {
      const msg =
        err?.response?.data?.detail?.message ||
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong. Please try again.";
      setErrorMessage(typeof msg === "string" ? msg : JSON.stringify(msg));
      setAppState(STATE.ERROR);
    }
  };

  const handleReset = () => {
    setResults(null);
    setAppState(STATE.IDLE);
    setErrorMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const r = results || {};

  return (
    <div style={{ minHeight: "100vh", backgroundColor: COLORS.canvas }}>
      <header
        style={{
          borderBottom: `1px solid ${COLORS.hairline}66`,
          position: "sticky",
          top: 0,
          zIndex: 50,
          backgroundColor: `${COLORS.canvas}cc`,
          WebkitBackdropFilter: "blur(12px)",
          backdropFilter: "blur(12px)",
        }}
      >
        <div
          style={{
            maxWidth: 1199,
            margin: "0 auto",
            padding: "14px 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: RADIUS.md,
                backgroundColor: COLORS["surface-1"],
                border: `1px solid ${COLORS.hairline}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: COLORS.ink,
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </div>
            <div>
              <span style={{ fontSize: "15px", fontWeight: 600, color: COLORS.ink, letterSpacing: "-0.15px" }}>
                AI Recruiter Intelligence
              </span>
            </div>
            <Badge
              variant="optional"
              label="Powered by LLM Evaluation Engine"
              style={{ fontSize: "9px", padding: "3px 8px", opacity: 0.7, letterSpacing: "0.04em" }}
            />
          </div>

          {appState === STATE.RESULTS && (
            <Button id="new-analysis-btn" variant="secondary" onClick={handleReset}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
              </svg>
              New Analysis
            </Button>
          )}
        </div>
      </header>

      <main style={{ maxWidth: 1199, margin: "0 auto", padding: "48px 24px" }}>
        {appState === STATE.IDLE && (
          <div style={{ textAlign: "center", marginBottom: 48, animation: "fadeIn 0.5s ease" }}>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 16px",
                borderRadius: RADIUS.pill,
                fontSize: "12px",
                fontWeight: 600,
                letterSpacing: "-0.12px",
                backgroundColor: `${COLORS["surface-2"]}`,
                border: `1px solid ${COLORS.hairline}`,
                color: COLORS["ink-muted"],
                marginBottom: 24,
              }}
            >
              <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: COLORS["accent-blue"] }} />
              Powered by Gemini AI + Sentence Transformers
            </div>

            <h1
              style={{
                fontSize: "48px",
                fontWeight: 700,
                lineHeight: 1.1,
                letterSpacing: "-2.4px",
                color: COLORS.ink,
                fontFamily: TYPOGRAPHY.fontFamily.display,
                margin: "0 0 16px",
              }}
              className="max-md:text-[36px] max-sm:text-[28px]"
            >
              AI Resume Intelligence Platform
            </h1>

            <p
              style={{
                fontSize: "16px",
                color: COLORS["ink-muted"],
                lineHeight: 1.6,
                maxWidth: 560,
                margin: "0 auto",
                letterSpacing: "-0.16px",
              }}
            >
              Evaluate resumes like a senior AI recruiter using LLM reasoning, skill intelligence, semantic matching, and evidence-based scoring.
            </p>
          </div>
        )}

        {(appState === STATE.IDLE || appState === STATE.ERROR) && (
          <div style={{ animation: "slideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1)" }}>
            <UploadForm onSubmit={handleAnalyse} isLoading={false} />
            {appState === STATE.ERROR && (
              <div
                id="error-message"
                style={{
                  marginTop: SPACING.lg,
                  padding: SPACING.md,
                  borderRadius: RADIUS.lg,
                  backgroundColor: `${COLORS.semantic.error}12`,
                  border: `1px solid ${COLORS.semantic.error}25`,
                  color: COLORS.semantic.error,
                  fontSize: "14px",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 10,
                  animation: "slideDown 0.3s cubic-bezier(0.22, 1, 0.36, 1)",
                }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
                <span>{errorMessage}</span>
              </div>
            )}
          </div>
        )}

        {appState === STATE.LOADING && (
          <Card variant="default" style={{ padding: SPACING.xxl }}>
            <LoadingSpinner />
          </Card>
        )}

        {appState === STATE.RESULTS && results && (
          <div id="results-section" style={{ display: "flex", flexDirection: "column", gap: SPACING.xl, animation: "fadeIn 0.6s ease" }}>
            {results.fallback_mode && (
              <FallbackBanner />
            )}

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "280px 1fr",
                gap: SPACING.xl,
              }}
              className="max-lg:grid-cols-1"
            >
              <Card variant="default" style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: SPACING.sm }}>
                <span
                  style={{
                    fontSize: TYPOGRAPHY.micro.fontSize,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.12em",
                    color: COLORS["ink-muted"],
                    textAlign: "center",
                  }}
                >
                  Overall Match
                </span>
                <ScoreGauge score={r.match_score} />
              </Card>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: SPACING.md,
                }}
                className="max-sm:grid-cols-1"
              >
                <MetricCard
                  label="Matched Skills"
                  value={r.matched_skills?.length || 0}
                  sub="matched competencies"
                  accent="emerald"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  }
                />
                <MetricCard
                  label="Skill Gaps"
                  value={(r.critical_gaps?.length || 0) + (r.recommended_improvements?.length || 0) + (r.optional_skills?.length || 0) || r.missing_skills?.length || 0}
                  sub="missing JD skills"
                  accent="red"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="15" y1="9" x2="9" y2="15" />
                      <line x1="9" y1="9" x2="15" y2="15" />
                    </svg>
                  }
                />
                <MetricCard
                  label="Skill Overlap"
                  value={`${r.skill_overlap_score?.toFixed(0) || 0}%`}
                  sub="of JD skills covered"
                  accent="brand"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                    </svg>
                  }
                />
                <MetricCard
                  label="Semantic Similarity"
                  value={`${r.semantic_similarity_score?.toFixed(0) || 0}%`}
                  sub="content relevance"
                  accent="blue"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    </svg>
                  }
                />
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: SPACING.xl,
              }}
              className="max-md:grid-cols-1"
            >
              {r.candidate_level && (
                <Card variant="default" style={{ display: "flex", alignItems: "flex-start", gap: SPACING.md }}>
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: RADIUS.md,
                      backgroundColor: `${COLORS["accent-blue"]}15`,
                      border: `1px solid ${COLORS["accent-blue"]}20`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: COLORS["accent-blue"],
                      flexShrink: 0,
                    }}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  </div>
                  <div>
                    <span
                      style={{
                        fontSize: TYPOGRAPHY.micro.fontSize,
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.12em",
                        color: COLORS["ink-muted"],
                        display: "block",
                        marginBottom: 4,
                      }}
                    >
                      Seniority Assessment
                    </span>
                    <h3 style={{ fontSize: "18px", fontWeight: 700, color: COLORS.ink, margin: "0 0 6px", letterSpacing: "-0.18px" }}>
                      {r.candidate_level.candidate_level}
                    </h3>
                    <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: 0, lineHeight: 1.5, opacity: 0.7 }}>
                      {r.candidate_level.reason}
                    </p>
                  </div>
                </Card>
              )}

              {r.confidence && (
                <Card variant="default" style={{ display: "flex", alignItems: "flex-start", gap: SPACING.md }}>
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: RADIUS.md,
                      backgroundColor: `${getConfidenceColor(r.confidence.confidence_level)}15`,
                      border: `1px solid ${getConfidenceColor(r.confidence.confidence_level)}20`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: getConfidenceColor(r.confidence.confidence_level),
                      flexShrink: 0,
                    }}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                  </div>
                  <div>
                    <span
                      style={{
                        fontSize: TYPOGRAPHY.micro.fontSize,
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.12em",
                        color: COLORS["ink-muted"],
                        display: "block",
                        marginBottom: 4,
                      }}
                    >
                      Evaluation Confidence
                    </span>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <h3 style={{ fontSize: "18px", fontWeight: 700, color: COLORS.ink, margin: 0, letterSpacing: "-0.18px" }}>
                        {r.confidence.confidence_score}%
                      </h3>
                      <ConfidenceBadge level={r.confidence.confidence_level} />
                    </div>
                    <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: 0, lineHeight: 1.5, opacity: 0.7 }}>
                      Based on resume evidence context depth, project description verbal strength, and technical matching indicators.
                    </p>
                  </div>
                </Card>
              )}
            </div>

            <SkillBadges
              matched={r.matched_skills}
              criticalGaps={r.critical_gaps || []}
              recommendedImprovements={r.recommended_improvements || []}
              optionalSkills={r.optional_skills || []}
            />

            <ExplanationCard
              explanation={r.explanation}
              hiringRecommendation={r.hiring_recommendation}
              strengths={r.strengths}
              weaknesses={r.weaknesses}
              skillOverlapScore={r.skill_overlap_score}
              semanticScore={r.semantic_similarity_score}
            />

            <SuggestionsList suggestions={r.suggestions} />

            <div style={{ display: "flex", justifyContent: "center", paddingTop: SPACING.md }}>
              <Button onClick={handleReset} variant="primary" style={{ padding: "14px 36px" }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="23 4 23 10 17 10" />
                  <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
                </svg>
                Analyze Another Resume
              </Button>
            </div>
          </div>
        )}
      </main>

      <footer
        style={{
          borderTop: `1px solid ${COLORS.hairline}40`,
          marginTop: SPACING.section,
          padding: "32px 24px",
          textAlign: "center",
        }}
      >
        <p style={{ fontSize: "11px", color: COLORS["ink-muted"], opacity: 0.4, margin: 0, letterSpacing: "-0.11px" }}>
          Built with FastAPI &middot; Gemini AI &middot; Sentence Transformers &middot; React &middot; Tailwind CSS
        </p>
      </footer>
    </div>
  );
}

function getConfidenceColor(level) {
  if (!level) return COLORS["ink-muted"];
  const lc = level.toUpperCase();
  if (lc === "HIGH") return COLORS["semantic-success"];
  if (lc === "MEDIUM") return COLORS.semantic.warning;
  return COLORS.semantic.error;
}

function ConfidenceBadge({ level }) {
  if (!level) return null;
  const lc = level.toUpperCase();
  const color = getConfidenceColor(level);
  return (
    <span
      style={{
        fontSize: "9px",
        fontWeight: 800,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        padding: "3px 10px",
        borderRadius: RADIUS.sm,
        backgroundColor: `${color}20`,
        color,
        border: `1px solid ${color}30`,
      }}
    >
      {lc}
    </span>
  );
}

function FallbackBanner() {
  return (
    <Card
      variant="default"
      style={{
        padding: SPACING.md,
        backgroundColor: `${COLORS.semantic.warning}08`,
        border: `1px solid ${COLORS.semantic.warning}25`,
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: SPACING.sm }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={COLORS.semantic.warning} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <div>
          <h4 style={{ fontSize: "14px", fontWeight: 700, color: COLORS.ink, margin: "0 0 4px", letterSpacing: "-0.14px" }}>
            Gemini API Key Access Restricted (Fallback Mode Active)
          </h4>
          <p style={{ fontSize: "13px", color: COLORS["ink-muted"], lineHeight: 1.5, margin: 0, letterSpacing: "-0.13px" }}>
            Your Gemini API key or Google Cloud project returned a <strong>403 Permission Denied</strong> error. To ensure the app remains fully functional, we have activated our <strong>local keyword-based heuristic pipeline</strong>.
          </p>
          <p style={{ fontSize: "11px", color: COLORS["ink-muted"], marginTop: 8, lineHeight: 1.5, opacity: 0.7 }}>
            To resolve: Verify billing, confirm age verification at{" "}
            <a href="https://myaccount.google.com/age-verification" target="_blank" rel="noopener noreferrer" style={{ color: COLORS["accent-blue"], textDecoration: "underline" }}>
              myaccount.google.com/age-verification
            </a>, or generate a new API key in a new project on{" "}
            <a href="https://aistudio.google.com/" target="_blank" rel="noopener noreferrer" style={{ color: COLORS["accent-blue"], textDecoration: "underline" }}>
              Google AI Studio
            </a>.
          </p>
        </div>
      </div>
    </Card>
  );
}
