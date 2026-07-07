import React from "react";
import { Card } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

const DECISION_CONFIG = {
  "Strong Interview Candidate": {
    color: COLORS["semantic-success"],
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    ),
  },
  "Potential Candidate": {
    color: COLORS.semantic.warning,
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
      </svg>
    ),
  },
  "Needs Development": {
    color: COLORS.semantic.error,
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
    ),
  },
};

const RISK_CONFIG = {
  Low: { color: COLORS["semantic-success"], label: "Low Risk" },
  Medium: { color: COLORS.semantic.warning, label: "Medium Risk" },
  High: { color: COLORS.semantic.error, label: "High Risk" },
};

export default function RecruiterDecisionCard({ recruiterDecision }) {
  if (!recruiterDecision) return null;

  const { decision, risk_level, reasons = [], candidate_level } = recruiterDecision;

  const config = DECISION_CONFIG[decision] || DECISION_CONFIG["Potential Candidate"];
  const riskConfig = RISK_CONFIG[risk_level] || RISK_CONFIG["Medium"];

  return (
    <Card
      variant="default"
      id="recruiter-decision-card"
      style={{
        border: `1px solid ${config.color}25`,
        background: `linear-gradient(135deg, ${config.color}06 0%, transparent 60%)`,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: RADIUS.md,
            backgroundColor: `${config.color}15`,
            border: `1px solid ${config.color}25`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: config.color,
            flexShrink: 0,
          }}
        >
          {config.icon}
        </div>
        <div>
          <span
            style={{
              fontSize: TYPOGRAPHY.caption.fontSize,
              fontWeight: TYPOGRAPHY.caption.fontWeight,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: COLORS["ink-muted"],
              display: "block",
            }}
          >
            Recruiter Decision
          </span>
          <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
            AI-powered hiring recommendation
          </p>
        </div>
      </div>

      {/* Decision + Risk Row */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: SPACING.md,
          padding: SPACING.md,
          borderRadius: RADIUS.lg,
          backgroundColor: `${config.color}08`,
          border: `1px solid ${config.color}15`,
          marginBottom: SPACING.md,
          flexWrap: "wrap",
        }}
      >
        <h3
          style={{
            fontSize: "20px",
            fontWeight: 700,
            color: config.color,
            margin: 0,
            letterSpacing: "-0.3px",
            flex: 1,
          }}
        >
          {decision}
        </h3>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          {candidate_level && (
            <span
              style={{
                padding: "3px 10px",
                borderRadius: RADIUS.pill,
                fontSize: "11px",
                fontWeight: 600,
                backgroundColor: `${COLORS["accent-blue"]}15`,
                color: COLORS["accent-blue"],
                border: `1px solid ${COLORS["accent-blue"]}25`,
              }}
            >
              {candidate_level}
            </span>
          )}
          <span
            style={{
              padding: "3px 10px",
              borderRadius: RADIUS.pill,
              fontSize: "11px",
              fontWeight: 700,
              backgroundColor: `${riskConfig.color}15`,
              color: riskConfig.color,
              border: `1px solid ${riskConfig.color}25`,
            }}
          >
            {riskConfig.label}
          </span>
        </div>
      </div>

      {/* Reasons */}
      {reasons.length > 0 && (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 8 }}>
          {reasons.map((reason, i) => (
            <li
              key={i}
              style={{
                fontSize: "13px",
                color: COLORS["ink-muted"],
                lineHeight: 1.5,
                display: "flex",
                alignItems: "flex-start",
                gap: 8,
              }}
            >
              <span
                style={{
                  marginTop: 5,
                  flexShrink: 0,
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  backgroundColor: `${config.color}60`,
                }}
              />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
