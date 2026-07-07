import React, { useState } from "react";
import LoadingSpinner from "./components/LoadingSpinner";
import UploadForm from "./components/UploadForm";
import AnalysisDashboard from "./components/analysis/AnalysisDashboard";
import AIAnalysisProgress from "./components/analysis/AIAnalysisProgress";
import ResumePreview from "./components/preview/ResumePreview";
import JDPreview from "./components/preview/JDPreview";
import { Card, Button, Badge } from "./components/ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "./styles/designTokens";
import { analyzeResume, downloadReport } from "./services/api";

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
  const [activeResumeFile, setActiveResumeFile] = useState(null);
  const [activeJdText, setActiveJdText] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [apiFinished, setApiFinished] = useState(false);
  const [apiError, setApiError] = useState(false);

  const handleDownloadReport = async () => {
    if (!results) return;
    setIsDownloading(true);
    try {
      const blob = await downloadReport(results);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'AI_Recruiter_Report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Failed to download report", err);
      alert("Failed to download report. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  const handleAnalyse = async (resumeFile, jdText) => {
    setAppState(STATE.LOADING);
    setErrorMessage("");
    setApiFinished(false);
    setApiError(false);
    setActiveResumeFile(resumeFile);
    setActiveJdText(jdText);
    
    try {
      const data = await analyzeResume(resumeFile, jdText);
      setResults(data);
      setApiFinished(true); // Triggers AIAnalysisProgress onComplete
    } catch (err) {
      const msg =
        err?.response?.data?.detail?.message ||
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong. Please try again.";
      setErrorMessage(typeof msg === "string" ? msg : JSON.stringify(msg));
      setApiError(true);
    }
  };

  const handleReset = () => {
    setResults(null);
    setAppState(STATE.IDLE);
    setErrorMessage("");
    setApiFinished(false);
    setApiError(false);
    setActiveResumeFile(null);
    setActiveJdText("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

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
              label="AI Recruiter Intelligence Platform"
              style={{ fontSize: "9px", padding: "3px 8px", opacity: 0.7, letterSpacing: "0.04em" }}
            />
          </div>

          {appState === STATE.RESULTS && (
            <div style={{ display: "flex", gap: 12 }}>
              <Button 
                variant="primary" 
                onClick={handleDownloadReport} 
                disabled={isDownloading}
              >
                {isDownloading ? (
                  <LoadingSpinner size={14} color="currentColor" />
                ) : (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                )}
                {isDownloading ? "Generating..." : "Download Report"}
              </Button>
              <Button id="new-analysis-btn" variant="secondary" onClick={handleReset}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="23 4 23 10 17 10" />
                  <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
                </svg>
                New Analysis
              </Button>
            </div>
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
              Advanced Candidate Matching System
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
          <div style={{ display: "flex", flexDirection: "column", gap: SPACING.xl }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: SPACING.xl }} className="max-md:grid-cols-1">
              <ResumePreview resumeFile={activeResumeFile} />
              <JDPreview jdText={activeJdText} />
            </div>
            <AIAnalysisProgress 
              isApiComplete={apiFinished}
              isError={apiError}
              errorMessage={errorMessage}
              onComplete={() => {
                setAppState(STATE.RESULTS);
                setTimeout(() => document.getElementById("results-section")?.scrollIntoView({ behavior: "smooth" }), 100);
              }}
              onRetry={() => handleAnalyse(activeResumeFile, activeJdText)}
            />
          </div>
        )}

        {appState === STATE.RESULTS && results && (
          <div style={{ display: "flex", flexDirection: "column", gap: SPACING.xl, animation: "fadeIn 0.6s ease" }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: SPACING.xl,
              }}
              className="max-md:grid-cols-1"
            >
              <ResumePreview resumeFile={activeResumeFile} />
              <JDPreview jdText={activeJdText} matchedSkills={results.matched_skills} missingSkills={results.missing_skills} />
            </div>

            <AnalysisDashboard results={results} />
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
          AI Recruiter Intelligence &middot; Resume Analysis Engine &middot; Candidate Evaluation Platform
        </p>
      </footer>
    </div>
  );
}
