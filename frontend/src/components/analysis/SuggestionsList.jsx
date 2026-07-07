import React from "react";
import { Card } from "../ui";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../../styles/designTokens";

export default function SuggestionsList({ suggestions = [] }) {
  if (!suggestions.length) return null;

  return (
    <Card variant="default" id="suggestions-section">
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm, marginBottom: SPACING.lg }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["ink-muted"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 20V10" />
          <path d="M18 20V4" />
          <path d="M6 20v-4" />
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
            Improvement Plan
          </span>
          <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: "2px 0 0", opacity: 0.6 }}>
            Actionable steps to strengthen your application
          </p>
        </div>
      </div>

      <ol style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: SPACING.sm }}>
        {suggestions.map((suggestion, index) => (
          <li
            key={index}
            id={`suggestion-${index + 1}`}
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: SPACING.sm,
              padding: SPACING.md,
              borderRadius: RADIUS.lg,
              border: `1px solid ${COLORS.hairline}`,
              transition: "border-color 0.2s ease, background-color 0.2s ease",
            }}
            className="hover:border-[var(--hover-border)] hover:bg-[var(--hover-bg)]"
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = `${COLORS["accent-blue"]}30`;
              e.currentTarget.style.backgroundColor = `${COLORS["accent-blue"]}06`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = COLORS.hairline;
              e.currentTarget.style.backgroundColor = "transparent";
            }}
          >
            <span
              style={{
                flexShrink: 0,
                width: 24,
                height: 24,
                borderRadius: "50%",
                backgroundColor: `${COLORS["accent-blue"]}18`,
                color: COLORS["accent-blue"],
                fontSize: "11px",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginTop: 2,
              }}
            >
              {index + 1}
            </span>
            <div style={{ flex: 1 }}>
              <span style={{ fontSize: "14px", color: COLORS.ink, lineHeight: 1.5, letterSpacing: "-0.14px" }}>
                {suggestion}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </Card>
  );
}
