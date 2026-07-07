import React from "react";
import { Card, Badge } from "./ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../styles/designTokens";

export default function SkillBadges({
  matched = [],
  missing = [],
  criticalGaps = [],
  recommendedImprovements = [],
  optionalSkills = []
}) {
  let critical = criticalGaps;
  let recommended = recommendedImprovements;
  let optional = optionalSkills;

  if (critical.length === 0 && recommended.length === 0 && optional.length === 0 && missing.length > 0) {
    critical = missing.filter(item => typeof item === "object" && item.importance?.toUpperCase() === "CRITICAL");
    recommended = missing.filter(item => typeof item === "object" && item.importance?.toUpperCase() === "IMPORTANT");
    optional = missing.filter(item => typeof item === "object" && item.importance?.toUpperCase() === "OPTIONAL");
    const others = missing.filter(item => typeof item !== "object" || !["CRITICAL", "IMPORTANT", "OPTIONAL"].includes(item.importance?.toUpperCase()));
    recommended = [...recommended, ...others];
  }

  const totalMissingCount = critical.length + recommended.length + optional.length;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: SPACING.xl,
      }}
      className="max-lg:grid-cols-1"
    >
      <Card variant="default" id="matched-skills-section">
        <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["semantic-success"]} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
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
              Matched Skills{" "}
              <span style={{ color: COLORS["semantic-success"], letterSpacing: 0, fontWeight: 700 }}>({matched.length})</span>
            </span>
            <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
              Skills found in both resume and JD
            </p>
          </div>
        </div>

        {matched.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: SPACING.sm }}>
            {matched.map((item, idx) => {
              const isObj = typeof item === "object" && item !== null;
              const skillName = isObj ? item.skill : item;
              const category = isObj ? item.category : "Technical Skill";
              const evidence = isObj ? item.evidence : "";
              const reqSkill = isObj ? item.required_skill : "";
              const candSkill = isObj ? item.candidate_skill : "";
              const matchType = isObj ? item.match_type : "EXACT_MATCH";

              let displayName = skillName;
              if (reqSkill && candSkill && reqSkill !== candSkill) {
                displayName = `${reqSkill} (via ${candSkill})`;
              } else if (reqSkill) {
                displayName = reqSkill;
              }

              let badgeVariant = "exact";
              if (matchType === "EQUIVALENT_MATCH" || matchType === "EQUIVALENT") {
                badgeVariant = "equivalent";
              } else if (matchType === "PARTIAL_MATCH" || matchType === "PARTIAL") {
                badgeVariant = "partial";
              }

              return (
                <div
                  key={idx}
                  style={{
                    padding: SPACING.sm,
                    borderRadius: RADIUS.lg,
                    backgroundColor: `${COLORS["semantic-success"]}08`,
                    border: `1px solid ${COLORS["semantic-success"]}14`,
                    transition: "border-color 0.2s ease",
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = `${COLORS["semantic-success"]}2e`; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = `${COLORS["semantic-success"]}14`; }}
                >
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: SPACING.xs }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                        <span
                          style={{
                            fontSize: "14px",
                            fontWeight: 700,
                            color: COLORS["semantic-success"],
                            letterSpacing: "-0.14px",
                          }}
                        >
                          {displayName}
                        </span>
                        <Badge variant={badgeVariant} />
                        <span
                          style={{
                            fontSize: "9px",
                            fontWeight: 700,
                            textTransform: "uppercase",
                            letterSpacing: "0.08em",
                            padding: "2px 8px",
                            borderRadius: RADIUS.xs,
                            backgroundColor: `${COLORS["ink-muted"]}1a`,
                            color: COLORS["ink-muted"],
                            border: `1px solid ${COLORS["ink-muted"]}14`,
                          }}
                        >
                          {category}
                        </span>
                      </div>
                    </div>
                  </div>
                  {evidence && (
                    <p
                      style={{
                        fontSize: "12px",
                        color: COLORS["ink-muted"],
                        fontStyle: "italic",
                        margin: "8px 0 0",
                        lineHeight: 1.5,
                        opacity: 0.7,
                      }}
                    >
                      &ldquo;{evidence}&rdquo;
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ fontSize: "13px", color: COLORS["ink-muted"], fontStyle: "italic" }}>No skills matched.</p>
        )}
      </Card>

      <Card variant="default" id="missing-skills-section">
        <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS.semantic.error} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
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
              Missing Skills{" "}
              <span style={{ color: COLORS.semantic.error, letterSpacing: 0, fontWeight: 700 }}>({totalMissingCount})</span>
            </span>
            <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
              Skills required by the JD not found
            </p>
          </div>
        </div>

        {totalMissingCount > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: SPACING.md }}>
            {critical.length > 0 && (
              <SkillGroup
                title="Critical Gaps"
                count={critical.length}
                color={COLORS.semantic.error}
                items={critical}
                badgeVariant="critical"
              />
            )}
            {recommended.length > 0 && (
              <SkillGroup
                title="Recommended"
                count={recommended.length}
                color={COLORS.semantic.warning}
                items={recommended}
                badgeVariant="recommended"
              />
            )}
            {optional.length > 0 && (
              <SkillGroup
                title="Optional"
                count={optional.length}
                color={COLORS["ink-muted"]}
                items={optional}
                badgeVariant="optional"
              />
            )}
          </div>
        ) : (
          <p style={{ fontSize: "13px", color: COLORS["ink-muted"], fontStyle: "italic" }}>No missing skills — great coverage!</p>
        )}
      </Card>
    </div>
  );
}

function SkillGroup({ title, count, color, items, badgeVariant }) {
  return (
    <div>
      <h4
        style={{
          fontSize: "11px",
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color,
          margin: "0 0 8px",
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: color, flexShrink: 0 }} />
        {title} ({count})
      </h4>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {items.map((item, idx) => {
          const isObj = typeof item === "object" && item !== null;
          const skillName = isObj ? item.skill : item;
          const importance = isObj ? item.importance?.toUpperCase() : "IMPORTANT";
          const note = isObj ? item.note : "";

          return (
            <div
              key={idx}
              style={{
                padding: "10px 12px",
                borderRadius: RADIUS.lg,
                backgroundColor: `${color}08`,
                border: `1px solid ${color}15`,
                transition: "border-color 0.2s ease",
              }}
              className="hover:border-[var(--hover-color)]"
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = `${color}30`; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = `${color}15`; }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                <span
                  style={{
                    fontSize: "14px",
                    fontWeight: 700,
                    color: COLORS.ink,
                    letterSpacing: "-0.14px",
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  {skillName}
                </span>
                <Badge variant={badgeVariant} label={importance} />
              </div>
              {note && (
                <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "6px 0 0", lineHeight: 1.5, opacity: 0.7 }}>
                  {note}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
