import React, { useState } from "react";
import { Card } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

const PRIORITY_CONFIG = {
  CRITICAL: { color: COLORS.semantic.error, label: "Critical" },
  IMPORTANT: { color: COLORS.semantic.warning, label: "Important" },
  OPTIONAL: { color: COLORS["ink-muted"], label: "Optional" },
};

function ImprovementItem({ item, index }) {
  const [copied, setCopied] = useState(false);
  const priority = (item.priority || "IMPORTANT").toUpperCase();
  const config = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG["IMPORTANT"];

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(item.suggestion || "").then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div
      style={{
        padding: `${SPACING.sm} ${SPACING.md}`,
        borderRadius: RADIUS.lg,
        backgroundColor: `${config.color}06`,
        border: `1px solid ${config.color}18`,
        transition: "border-color 0.2s ease",
        position: "relative",
      }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = `${config.color}30`; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = `${config.color}18`; }}
    >
      {/* Top row: skill name + priority badge + copy button */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: SPACING.xs,
          marginBottom: 8,
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              fontSize: "14px",
              fontWeight: 700,
              color: COLORS.ink,
              letterSpacing: "-0.14px",
            }}
          >
            {index + 1}. {item.missing_skill}
          </span>
          <span
            style={{
              fontSize: "9px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              padding: "2px 7px",
              borderRadius: RADIUS.xs,
              backgroundColor: `${config.color}15`,
              color: config.color,
              border: `1px solid ${config.color}25`,
              flexShrink: 0,
            }}
          >
            {config.label}
          </span>
        </div>

        {/* Copy to clipboard button */}
        <button
          onClick={handleCopy}
          title="Copy suggestion to clipboard"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            padding: "3px 8px",
            borderRadius: RADIUS.sm,
            border: `1px solid ${COLORS.hairline}`,
            backgroundColor: copied ? `${COLORS["semantic-success"]}10` : "transparent",
            color: copied ? COLORS["semantic-success"] : COLORS["ink-muted"],
            cursor: "pointer",
            fontSize: "10px",
            fontWeight: 600,
            transition: "all 0.2s ease",
            letterSpacing: "0.02em",
            flexShrink: 0,
          }}
        >
          {copied ? (
            <>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Copied
            </>
          ) : (
            <>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
              </svg>
              Copy
            </>
          )}
        </button>
      </div>

      {/* Suggestion text — styled as a resume snippet */}
      {item.suggestion && (
        <div
          style={{
            fontSize: "12px",
            color: COLORS["ink-muted"],
            lineHeight: 1.6,
            fontStyle: "italic",
            backgroundColor: `${COLORS["surface-1"]}80`,
            border: `1px solid ${COLORS.hairline}`,
            borderRadius: RADIUS.sm,
            padding: "8px 10px",
          }}
        >
          {item.suggestion}
        </div>
      )}
    </div>
  );
}

export default function ImprovementPlan({ improvementPlan = [], suggestions = [] }) {
  // Prefer structured improvement_plan from backend, fallback to generic suggestions
  const hasStructured = improvementPlan && improvementPlan.length > 0;
  const critical = hasStructured ? improvementPlan.filter(i => (i.priority || "").toUpperCase() === "CRITICAL") : [];
  const important = hasStructured ? improvementPlan.filter(i => (i.priority || "").toUpperCase() === "IMPORTANT") : [];
  const optional = hasStructured ? improvementPlan.filter(i => (i.priority || "").toUpperCase() === "OPTIONAL") : [];

  const hasFallback = !hasStructured && suggestions.length > 0;
  const isEmpty = !hasStructured && !hasFallback;

  return (
    <Card variant="default" id="improvement-plan-section">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["accent-blue"]} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="20" x2="12" y2="10" />
          <line x1="18" y1="20" x2="18" y2="4" />
          <line x1="6" y1="20" x2="6" y2="16" />
        </svg>
        <div>
          <span
            style={{
              fontSize: TYPOGRAPHY.caption.fontSize,
              fontWeight: TYPOGRAPHY.caption.fontWeight,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: COLORS["ink-muted"],
            }}
          >
            Improvement Roadmap
          </span>
          <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
            {hasStructured
              ? `${improvementPlan.length} actionable resume improvements`
              : "AI-generated improvement suggestions"}
          </p>
        </div>
      </div>

      {isEmpty && (
        <p style={{ fontSize: "13px", color: COLORS["ink-muted"], fontStyle: "italic" }}>
          No specific improvements needed — strong skill coverage!
        </p>
      )}

      {/* Structured improvement plan (prioritized) */}
      {hasStructured && (
        <div
          className="custom-scrollbar"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: SPACING.sm,
            maxHeight: "500px",
            overflowY: "auto",
            paddingRight: "8px",
            maskImage: "linear-gradient(to bottom, black 90%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to bottom, black 90%, transparent 100%)",
            paddingBottom: "16px",
          }}
        >
          {/* Critical first */}
          {critical.length > 0 && (
            <div>
              <h4 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: COLORS.semantic.error, margin: "0 0 8px", display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: COLORS.semantic.error, flexShrink: 0 }} />
                Critical Gaps ({critical.length})
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {critical.map((item, i) => <ImprovementItem key={i} item={item} index={i} />)}
              </div>
            </div>
          )}

          {/* Important */}
          {important.length > 0 && (
            <div style={{ marginTop: critical.length > 0 ? SPACING.md : 0 }}>
              <h4 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: COLORS.semantic.warning, margin: "0 0 8px", display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: COLORS.semantic.warning, flexShrink: 0 }} />
                Recommended ({important.length})
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {important.map((item, i) => <ImprovementItem key={i} item={item} index={i} />)}
              </div>
            </div>
          )}

          {/* Optional */}
          {optional.length > 0 && (
            <div style={{ marginTop: important.length > 0 ? SPACING.md : 0 }}>
              <h4 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: COLORS["ink-muted"], margin: "0 0 8px", display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: COLORS["ink-muted"], flexShrink: 0 }} />
                Optional ({optional.length})
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {optional.map((item, i) => <ImprovementItem key={i} item={item} index={i} />)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Fallback: generic suggestions list */}
      {hasFallback && (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: SPACING.sm }}>
          {suggestions.map((s, i) => (
            <li
              key={i}
              style={{
                fontSize: "13px",
                color: COLORS["ink-muted"],
                lineHeight: 1.6,
                display: "flex",
                alignItems: "flex-start",
                gap: 8,
                padding: `${SPACING.xs} 0`,
                borderBottom: i < suggestions.length - 1 ? `1px solid ${COLORS.hairline}40` : "none",
              }}
            >
              <span
                style={{
                  marginTop: 5,
                  flexShrink: 0,
                  width: 5,
                  height: 5,
                  borderRadius: "50%",
                  backgroundColor: `${COLORS["accent-blue"]}60`,
                }}
              />
              <span>{s}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
