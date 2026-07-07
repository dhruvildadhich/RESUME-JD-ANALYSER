import React from "react";
import { Card } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

export default function ExplanationCard({
  explanation,
  hiringRecommendation,
  strengths = [],
  weaknesses = [],
  skillOverlapScore,
  semanticScore,
}) {
  const recMeta = getRecommendationMeta(hiringRecommendation);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: SPACING.xl }}>
      <Card variant="default">
        <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["ink-muted"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
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
              Score Breakdown
            </span>
            <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
              Component score overview
            </p>
          </div>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: SPACING.lg,
          }}
          className="max-sm:grid-cols-1"
        >
          <ScoreBar label="Skill Alignment"       value={skillOverlapScore} color={COLORS["accent-blue"]} />
          <ScoreBar label="Experience Relevance"   value={semanticScore}     color={COLORS["gradient-violet"]} />
        </div>
      </Card>

      <Card variant="default" id="explanation-card">
        <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["ink-muted"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
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
              Explanation
            </span>
            <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
              Detailed evaluation summary
            </p>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: SPACING.sm,
            padding: SPACING.md,
            borderRadius: RADIUS.lg,
            backgroundColor: `${recMeta.color}08`,
            border: `1px solid ${recMeta.color}15`,
            marginBottom: SPACING.lg,
          }}
        >
          {hiringRecommendation && (
            <span
              style={{
                display: "inline-flex",
                padding: "4px 12px",
                borderRadius: RADIUS.pill,
                fontSize: "11px",
                fontWeight: 700,
                letterSpacing: "-0.11px",
                backgroundColor: `${recMeta.color}18`,
                color: recMeta.color,
                border: `1px solid ${recMeta.color}25`,
                flexShrink: 0,
                marginTop: 1,
              }}
            >
              {hiringRecommendation}
            </span>
          )}
          <p style={{ fontSize: "14px", color: COLORS.ink, lineHeight: 1.6, margin: 0, letterSpacing: "-0.14px" }}>
            {explanation}
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: SPACING.md,
          }}
          className="max-md:grid-cols-1"
        >
          {strengths.length > 0 && (
            <ListCard
              id="strengths-card"
              title="Strengths"
              items={strengths}
              dotColor={COLORS["semantic-success"]}
            />
          )}
          {weaknesses.length > 0 && (
            <ListCard
              id="weaknesses-card"
              title="Areas to Improve"
              items={weaknesses}
              dotColor={COLORS.semantic.warning}
            />
          )}
        </div>
      </Card>
    </div>
  );
}

function getRecommendationMeta(rec) {
  if (!rec) return { color: COLORS["ink-muted"] };
  const lc = rec.toLowerCase();
  if (lc.includes("strong")) return { color: COLORS["semantic-success"] };
  if (lc.includes("good") || lc.includes("potential") || lc === "hire") return { color: COLORS["accent-blue"] };
  if (lc.includes("neutral") || lc.includes("needs") || lc.includes("improve")) return { color: COLORS.semantic.warning };
  return { color: COLORS.semantic.error };
}

function ScoreBar({ label, value, color }) {
  const pct = Math.min(100, Math.max(0, value || 0));
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <span style={{ fontSize: "12px", color: COLORS["ink-muted"] }}>{label}</span>
        <span style={{ fontSize: "13px", fontWeight: 700, color: COLORS.ink }}>
          {Math.round(pct)}%
        </span>
      </div>
      <div
        style={{
          height: 4,
          backgroundColor: COLORS["surface-2"],
          borderRadius: RADIUS.full,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            backgroundColor: color,
            borderRadius: RADIUS.full,
            transition: "width 1s cubic-bezier(0.22, 1, 0.36, 1)",
          }}
        />
      </div>
    </div>
  );
}

function ListCard({ id, title, items, dotColor }) {
  if (!items || items.length === 0) return null;

  return (
    <div
      id={id}
      style={{
        padding: SPACING.md,
        borderRadius: RADIUS.lg,
        border: `1px solid ${COLORS.hairline}`,
        backgroundColor: `${dotColor}06`,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: SPACING.sm }}>
        <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: dotColor, flexShrink: 0 }} />
        <span
          style={{
            fontSize: TYPOGRAPHY.caption.fontSize,
            fontWeight: TYPOGRAPHY.caption.fontWeight,
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            color: COLORS["ink-muted"],
          }}
        >
          {title}
        </span>
      </div>
      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: "8px" }}>
        {items.map((item, i) => (
          <li
            key={i}
            style={{
              fontSize: "13px",
              color: COLORS.ink,
              lineHeight: 1.5,
              display: "flex",
              alignItems: "flex-start",
              gap: 8,
              letterSpacing: "-0.13px",
            }}
          >
            <span
              style={{
                marginTop: 6,
                flexShrink: 0,
                width: 4,
                height: 4,
                borderRadius: "50%",
                backgroundColor: `${dotColor}60`,
              }}
            />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
