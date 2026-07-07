import React from "react";
import { Card, Badge, AccordionCard } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

export default function MissingSkills({
  missing = [],
  criticalGaps = [],
  recommendedImprovements = [],
  optionalSkills = [],
}) {
  let critical    = criticalGaps;
  let recommended = recommendedImprovements;
  let optional    = optionalSkills;

  // Fallback: derive groups from flat missing[] list
  if (critical.length === 0 && recommended.length === 0 && optional.length === 0 && missing.length > 0) {
    critical    = missing.filter(i => typeof i === "object" && i.importance?.toUpperCase() === "CRITICAL");
    recommended = missing.filter(i => typeof i === "object" && i.importance?.toUpperCase() === "IMPORTANT");
    optional    = missing.filter(i => typeof i === "object" && i.importance?.toUpperCase() === "OPTIONAL");
    const others = missing.filter(i => typeof i !== "object" || !["CRITICAL", "IMPORTANT", "OPTIONAL"].includes(i.importance?.toUpperCase()));
    recommended  = [...recommended, ...others];
  }

  const totalMissingCount = critical.length + recommended.length + optional.length;

  return (
    <Card variant="default" id="missing-skills-section">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS.semantic.error} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <div>
          <span style={{ fontSize: TYPOGRAPHY.caption.fontSize, fontWeight: TYPOGRAPHY.caption.fontWeight, textTransform: "uppercase", letterSpacing: "0.12em", color: COLORS["ink-muted"] }}>
            Missing Skills{" "}
            <span style={{ color: COLORS.semantic.error, letterSpacing: 0, fontWeight: 700 }}>({totalMissingCount})</span>
          </span>
          <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
            Skills required by the JD not found
          </p>
        </div>
      </div>

      {totalMissingCount > 0 ? (
        <div
          className="custom-scrollbar"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: SPACING.sm,
            maxHeight: "440px",
            overflowY: "auto",
            paddingRight: "6px",
            maskImage: "linear-gradient(to bottom, black 90%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to bottom, black 90%, transparent 100%)",
            paddingBottom: "16px",
          }}
        >
          {critical.length > 0 && (
            <SkillGroup title="Critical Gaps" count={critical.length} color={COLORS.semantic.error} items={critical} badgeVariant="critical" />
          )}
          {recommended.length > 0 && (
            <SkillGroup title="Recommended" count={recommended.length} color={COLORS.semantic.warning} items={recommended} badgeVariant="recommended" />
          )}
          {optional.length > 0 && (
            <SkillGroup title="Optional" count={optional.length} color={COLORS["ink-muted"]} items={optional} badgeVariant="optional" />
          )}
        </div>
      ) : (
        <p style={{ fontSize: "13px", color: COLORS["ink-muted"], fontStyle: "italic" }}>No missing skills — great coverage!</p>
      )}
    </Card>
  );
}

function SkillGroup({ title, count, color, items, badgeVariant }) {
  return (
    <div>
      {/* Group label */}
      <h4 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color, margin: "0 0 6px", display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: color, flexShrink: 0 }} />
        {title} ({count})
      </h4>

      <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
        {items.map((item, idx) => {
          const isObj       = typeof item === "object" && item !== null;
          const skillName   = isObj ? item.skill                         : item;
          const importance  = isObj ? (item.importance?.toUpperCase() ?? "IMPORTANT") : "IMPORTANT";
          const note        = isObj ? item.note                          : "";
          const suggestion  = isObj ? item.suggestion                    : null;
          const impactScore = isObj ? item.impact_score                  : null;

          // ── Summary row (always visible) ────────────────────────
          const summary = (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
              {/* Skill name */}
              <span style={{ fontSize: "14px", fontWeight: 700, color: COLORS.ink, letterSpacing: "-0.14px" }}>
                {skillName}
              </span>

              <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
                {/* Impact score */}
                {impactScore != null && (
                  <span title={`Score impact: ${impactScore}`} style={{ fontSize: "9px", fontWeight: 700, letterSpacing: "0.04em", padding: "2px 7px", borderRadius: RADIUS.xs, backgroundColor: `${color}12`, color, border: `1px solid ${color}25`, flexShrink: 0 }}>
                    {impactScore > 0 ? "+" : ""}{impactScore}
                  </span>
                )}
                {/* Importance badge */}
                <Badge variant={badgeVariant} label={importance} />
              </div>
            </div>
          );

          // ── Expanded body ──────────────────────────────────────
          const hasBody = note || suggestion;
          const body = (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {note && (
                <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: 0, lineHeight: 1.5, opacity: 0.75 }}>
                  {note}
                </p>
              )}
              {suggestion && (
                <div style={{ padding: "7px 10px", borderRadius: RADIUS.sm, backgroundColor: `${COLORS["surface-1"]}80`, border: `1px solid ${COLORS.hairline}`, fontSize: "11px", color: COLORS["ink-muted"], lineHeight: 1.6, fontStyle: "italic" }}>
                  💡 {suggestion}
                </div>
              )}
              {!hasBody && (
                <p style={{ fontSize: "12px", color: COLORS["ink-muted"], fontStyle: "italic", margin: 0, opacity: 0.6 }}>
                  No additional context available.
                </p>
              )}
            </div>
          );

          return (
            <AccordionCard
              key={idx}
              accentColor={color}
              summary={summary}
            >
              {body}
            </AccordionCard>
          );
        })}
      </div>
    </div>
  );
}
