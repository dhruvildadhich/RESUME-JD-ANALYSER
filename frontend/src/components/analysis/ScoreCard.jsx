import React from "react";
import { Card, MetricCard, Badge } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";
import ScoreGauge from "../ScoreGauge";

function getConfidenceColor(level) {
  if (!level) return COLORS["ink-muted"];
  const lc = level.toUpperCase();
  if (lc === "HIGH") return COLORS["semantic-success"];
  if (lc === "MEDIUM") return COLORS.semantic.warning;
  return COLORS.semantic.error;
}

function ConfidenceBadge({ level }) {
  if (!level) return null;
  const color = getConfidenceColor(level);
  return (
    <div
      style={{
        padding: "3px 8px",
        borderRadius: RADIUS.xs,
        backgroundColor: `${color}15`,
        border: `1px solid ${color}30`,
        color,
        fontSize: "10px",
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        display: "inline-flex",
        alignItems: "center",
      }}
    >
      {level} CONFIDENCE
    </div>
  );
}

export default function ScoreCard({ r }) {
  if (!r) return null;

  return (
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
  );
}
