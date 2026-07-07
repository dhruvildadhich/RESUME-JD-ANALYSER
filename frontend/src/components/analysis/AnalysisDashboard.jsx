import React from "react";
import ScoreCard from "./ScoreCard";
import MatchedSkills from "./MatchedSkills";
import MissingSkills from "./MissingSkills";
import ExplanationCard from "./ExplanationCard";
import ImprovementPlan from "./ImprovementPlan";
import RecruiterDecisionCard from "./RecruiterDecisionCard";
import ConfidenceCard from "./ConfidenceCard";
import { SPACING, COLORS, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

export default function AnalysisDashboard({ results }) {
  if (!results) return null;

  return (
    <div id="results-section" style={{ display: "flex", flexDirection: "column", gap: SPACING.xl, animation: "fadeIn 0.6s ease" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: SPACING.xs }}>
        <h2 style={{ fontSize: "24px", fontWeight: 700, color: COLORS.ink, letterSpacing: "-0.48px", fontFamily: TYPOGRAPHY.fontFamily.display }}>
          AI Recruiter Intelligence
        </h2>
        <div style={{ height: 1, flex: 1, backgroundColor: `${COLORS.hairline}66` }} />
      </div>

      {results.fallback_mode && <FallbackBanner />}

      {/* 1. Recruiter Decision */}
      {results.recruiter_decision && (
        <RecruiterDecisionCard recruiterDecision={results.recruiter_decision} />
      )}

      {/* 2. Score Overview */}
      <ScoreCard r={results} />

      {/* 3. Confidence Analysis */}
      {results.confidence_analysis && (
        <ConfidenceCard confidenceAnalysis={results.confidence_analysis} />
      )}

      {/* 4. Matched / Missing Skills */}
      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: SPACING.xl }}
        className="max-md:grid-cols-1"
      >
        <MatchedSkills matched={results.matched_skills} />
        <MissingSkills
          missing={results.missing_skills}
          criticalGaps={results.critical_gaps}
          recommendedImprovements={results.recommended_improvements}
          optionalSkills={results.optional_skills}
        />
      </div>

      {/* 5. AI Recruiter Explanation */}
      <ExplanationCard
        explanation={results.explanation}
        hiringRecommendation={results.hiring_recommendation}
        strengths={results.strengths}
        weaknesses={results.weaknesses}
        skillOverlapScore={results.skill_overlap_score}
        semanticScore={results.semantic_similarity_score}
      />

      {/* 6. Improvement Roadmap */}
      <ImprovementPlan
        improvementPlan={results.improvement_plan}
        suggestions={results.suggestions}
      />
    </div>
  );
}

function FallbackBanner() {
  return (
    <div
      style={{
        padding: SPACING.md,
        backgroundColor: `${COLORS.semantic.warning}08`,
        border: `1px solid ${COLORS.semantic.warning}25`,
        borderRadius: RADIUS.lg,
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
            AI Service Operating in Compatibility Mode
          </h4>
          <p style={{ fontSize: "13px", color: COLORS["ink-muted"], lineHeight: 1.5, margin: 0, letterSpacing: "-0.13px" }}>
            The primary AI analysis service is temporarily unavailable. Results are being generated using our <strong>built-in evaluation pipeline</strong> to ensure uninterrupted service.
          </p>
        </div>
      </div>
    </div>
  );
}
