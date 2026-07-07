import React from "react";
import { Card, Badge, AccordionCard } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

export default function MatchedSkills({ matched = [] }) {
  return (
    <Card variant="default" id="matched-skills-section">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["semantic-success"]} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <div>
          <span style={{ fontSize: TYPOGRAPHY.caption.fontSize, fontWeight: TYPOGRAPHY.caption.fontWeight, textTransform: "uppercase", letterSpacing: "0.12em", color: COLORS["ink-muted"] }}>
            Matched Skills{" "}
            <span style={{ color: COLORS["semantic-success"], letterSpacing: 0, fontWeight: 700 }}>({matched.length})</span>
          </span>
          <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
            Skills found in both resume and JD
          </p>
        </div>
      </div>

      {matched.length > 0 ? (
        <div
          className="custom-scrollbar"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: SPACING.xs,
            maxHeight: "440px",
            overflowY: "auto",
            paddingRight: "6px",
            maskImage: "linear-gradient(to bottom, black 90%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to bottom, black 90%, transparent 100%)",
            paddingBottom: "16px",
          }}
        >
          {matched.map((item, idx) => {
            const isObj = typeof item === "object" && item !== null;
            const skillName       = isObj ? item.skill          : item;
            const category        = isObj ? item.category       : "Technical Skill";
            const evidence        = isObj ? item.evidence       : "";
            const reqSkill        = isObj ? item.required_skill : "";
            const candSkill       = isObj ? item.candidate_skill : "";
            const matchType       = isObj ? item.match_type     : "EXACT_MATCH";
            const experienceLevel = isObj ? item.experience_level : null;
            const confidence      = isObj ? item.confidence     : null;

            let displayName = skillName;
            if (reqSkill && candSkill && reqSkill !== candSkill) {
              displayName = `${reqSkill} (via ${candSkill})`;
            } else if (reqSkill) {
              displayName = reqSkill;
            }

            let badgeVariant = "exact";
            if (matchType === "EQUIVALENT_MATCH" || matchType === "EQUIVALENT") badgeVariant = "equivalent";
            else if (matchType === "PARTIAL_MATCH"    || matchType === "PARTIAL")    badgeVariant = "partial";

            const accentColor = COLORS["semantic-success"];

            // ── Summary row (always visible) ──────────────────────
            const summary = (
              <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                {/* Skill name */}
                <span style={{ fontSize: "14px", fontWeight: 700, color: accentColor, letterSpacing: "-0.14px" }}>
                  {displayName}
                </span>

                {/* Match type badge */}
                <Badge variant={badgeVariant} />

                {/* Experience level */}
                {experienceLevel && <ExperienceLevelBadge level={experienceLevel} />}

                {/* Category */}
                <span style={{ fontSize: "9px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", padding: "2px 8px", borderRadius: RADIUS.xs, backgroundColor: `${COLORS["ink-muted"]}1a`, color: COLORS["ink-muted"], border: `1px solid ${COLORS["ink-muted"]}14` }}>
                  {category}
                </span>

                {/* Confidence */}
                {confidence != null && (
                  <span style={{ fontSize: "9px", fontWeight: 700, letterSpacing: "0.04em", padding: "2px 7px", borderRadius: RADIUS.xs, backgroundColor: `${accentColor}12`, color: accentColor, border: `1px solid ${accentColor}20` }}>
                    {Math.round(confidence * 100)}%
                  </span>
                )}
              </div>
            );

            // ── Expanded body ──────────────────────────────────────
            const body = evidence ? (
              <div>
                <p style={{ fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: COLORS["ink-muted"], margin: "0 0 6px", opacity: 0.6 }}>
                  Resume Evidence
                </p>
                <p style={{ fontSize: "12px", color: COLORS["ink-muted"], fontStyle: "italic", margin: 0, lineHeight: 1.6, padding: "8px 10px", backgroundColor: `${COLORS["surface-1"]}80`, border: `1px solid ${COLORS.hairline}`, borderRadius: RADIUS.sm }}>
                  &ldquo;{evidence}&rdquo;
                </p>
              </div>
            ) : (
              <p style={{ fontSize: "12px", color: COLORS["ink-muted"], fontStyle: "italic", margin: 0, opacity: 0.6 }}>
                No detailed evidence available.
              </p>
            );

            return (
              <AccordionCard
                key={idx}
                accentColor={accentColor}
                summary={summary}
              >
                {body}
              </AccordionCard>
            );
          })}
        </div>
      ) : (
        <p style={{ fontSize: "13px", color: COLORS["ink-muted"], fontStyle: "italic" }}>No skills matched.</p>
      )}
    </Card>
  );
}

function ExperienceLevelBadge({ level }) {
  if (!level) return null;
  const configs = {
    "Production Experience": { color: COLORS["semantic-success"], stars: 3, short: "Production" },
    "Project Experience":    { color: COLORS["accent-blue"],       stars: 2, short: "Project"    },
    "Mention Only":          { color: COLORS["ink-muted"],         stars: 1, short: "Listed"     },
  };
  const cfg = configs[level] || configs["Mention Only"];
  return (
    <span
      title={level}
      style={{ display: "inline-flex", alignItems: "center", gap: 3, fontSize: "9px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", padding: "2px 7px", borderRadius: RADIUS.xs, backgroundColor: `${cfg.color}12`, color: cfg.color, border: `1px solid ${cfg.color}22`, flexShrink: 0 }}
    >
      {Array.from({ length: cfg.stars }).map((_, i) => (
        <svg key={i} width="7" height="7" viewBox="0 0 24 24" fill={cfg.color} stroke="none">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      ))}
      {" "}{cfg.short}
    </span>
  );
}
