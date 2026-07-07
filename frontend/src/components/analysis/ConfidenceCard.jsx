import React from "react";
import { Card } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

function getConfidenceConfig(level) {
  if (!level) return { color: COLORS["ink-muted"], label: "UNKNOWN" };
  const lc = level.toUpperCase();
  if (lc === "HIGH") return { color: COLORS["semantic-success"], label: "HIGH" };
  if (lc === "MEDIUM") return { color: COLORS.semantic.warning, label: "MEDIUM" };
  return { color: COLORS.semantic.error, label: "LOW" };
}

function CircularProgress({ score, color, size = 100 }) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`${color}18`}
          strokeWidth={10}
        />
        {/* Progress arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.22, 1, 0.36, 1)" }}
        />
      </svg>
      {/* Center label */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span style={{ fontSize: "20px", fontWeight: 700, color, letterSpacing: "-0.5px" }}>
          {score}%
        </span>
      </div>
    </div>
  );
}

export default function ConfidenceCard({ confidenceAnalysis }) {
  if (!confidenceAnalysis) return null;

  const { confidence_score, level, reasons = [] } = confidenceAnalysis;
  const config = getConfidenceConfig(level);

  return (
    <Card variant="default" id="confidence-analysis-card">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: RADIUS.md,
            backgroundColor: `${config.color}15`,
            border: `1px solid ${config.color}20`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: config.color,
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
              fontSize: TYPOGRAPHY.caption.fontSize,
              fontWeight: TYPOGRAPHY.caption.fontWeight,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: COLORS["ink-muted"],
              display: "block",
            }}
          >
            Analysis Confidence
          </span>
          <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
            Evidence-based reliability score
          </p>
        </div>
      </div>

      {/* Body: circular progress + reasons */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: SPACING.xl }}>
        {/* Circular gauge */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <CircularProgress score={confidence_score} color={config.color} size={96} />
          <span
            style={{
              fontSize: "10px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              padding: "2px 8px",
              borderRadius: RADIUS.xs,
              backgroundColor: `${config.color}15`,
              color: config.color,
              border: `1px solid ${config.color}25`,
            }}
          >
            {config.label} CONFIDENCE
          </span>
        </div>

        {/* Reasons */}
        <div style={{ flex: 1 }}>
          <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 9 }}>
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
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={config.color}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ flexShrink: 0, marginTop: 2 }}
                >
                  {reason.toLowerCase().includes("no ") || reason.toLowerCase().includes("lack") || reason.toLowerCase().includes("low") || reason.toLowerCase().includes("weak") || reason.toLowerCase().includes("several") ? (
                    <>
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </>
                  ) : (
                    <polyline points="20 6 9 17 4 12" />
                  )}
                </svg>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}
