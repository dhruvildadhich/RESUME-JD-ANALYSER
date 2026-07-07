import React from "react";
import { COLORS, RADIUS } from "../../styles/designTokens";

const variants = {
  exact: { bg: `${COLORS["semantic-success"]}26`, color: COLORS["semantic-success"], border: `${COLORS["semantic-success"]}33` },
  equivalent: { bg: `${COLORS["accent-blue"]}26`, color: COLORS["accent-blue"], border: `${COLORS["accent-blue"]}33` },
  partial: { bg: `${COLORS.semantic.warning}26`, color: COLORS.semantic.warning, border: `${COLORS.semantic.warning}33` },
  critical: { bg: `${COLORS.semantic.error}33`, color: COLORS.semantic.error, border: `${COLORS.semantic.error}40` },
  recommended: { bg: `${COLORS.semantic.warning}26`, color: COLORS.semantic.warning, border: `${COLORS.semantic.warning}33` },
  optional: { bg: `${COLORS["ink-muted"]}26`, color: COLORS["ink-muted"], border: `${COLORS["ink-muted"]}26` },
};

const labels = {
  exact: "EXACT",
  equivalent: "EQUIVALENT",
  partial: "PARTIAL",
  critical: "CRITICAL",
  recommended: "RECOMMENDED",
  optional: "OPTIONAL",
};

export default function Badge({ variant = "exact", label, className = "", style, ...props }) {
  const cfg = variants[variant] || variants.exact;
  const displayLabel = label || labels[variant] || variant;

  return (
    <span
      className={className}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 10px",
        borderRadius: RADIUS.sm,
        fontSize: "10px",
        fontWeight: 800,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        backgroundColor: cfg.bg,
        color: cfg.color,
        border: `1px solid ${cfg.border}`,
        ...style,
      }}
      {...props}
    >
      {displayLabel}
    </span>
  );
}
