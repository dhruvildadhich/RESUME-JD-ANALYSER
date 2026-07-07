import React from "react";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../../styles/designTokens";

const accentColors = {
  brand: { text: COLORS.ink, iconBg: `${COLORS.ink}1a` },
  emerald: { text: COLORS["semantic-success"], iconBg: `${COLORS["semantic-success"]}26` },
  red: { text: COLORS.semantic.error, iconBg: `${COLORS.semantic.error}26` },
  blue: { text: COLORS["accent-blue"], iconBg: `${COLORS["accent-blue"]}26` },
};

export default function MetricCard({ label, value, sub, icon, accent = "brand", className = "", style, ...props }) {
  const c = accentColors[accent] || accentColors.brand;

  return (
    <div
      className={className}
      style={{
        backgroundColor: COLORS["surface-1"],
        borderRadius: RADIUS.xl,
        padding: SPACING.lg,
        ...style,
      }}
      {...props}
    >
      <div style={{ display: "flex", alignItems: "center", gap: SPACING.xs, marginBottom: SPACING.sm }}>
        {icon && (
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: RADIUS.md,
              backgroundColor: c.iconBg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: c.text,
              flexShrink: 0,
            }}
          >
            {icon}
          </div>
        )}
        <span
          style={{
            fontSize: TYPOGRAPHY.caption.fontSize,
            fontWeight: TYPOGRAPHY.caption.fontWeight,
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            color: COLORS["ink-muted"],
          }}
        >
          {label}
        </span>
      </div>
      <p style={{ fontSize: "30px", fontWeight: 800, lineHeight: 1, color: c.text, margin: "0 0 4px" }}>{value}</p>
      {sub && <p style={{ fontSize: "12px", color: COLORS["ink-muted"], margin: 0 }}>{sub}</p>}
    </div>
  );
}
