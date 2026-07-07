import React from "react";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY, SHADOWS } from "../../styles/designTokens";
const PH_COLOR = COLORS["ink-muted"];

export default function Input({
  label,
  error,
  multiline = false,
  className = "",
  style,
  rows = 4,
  ...props
}) {
  const Tag = multiline ? "textarea" : "input";
  const [focused, setFocused] = React.useState(false);

  const id = React.useId();
  const uid = `input-${id}`;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: SPACING.xs }}>
      <style>{`.${uid}::placeholder{color:${PH_COLOR};opacity:0.6}`}</style>
      {label && (
        <label
          style={{
            fontSize: TYPOGRAPHY.caption.fontSize,
            fontWeight: TYPOGRAPHY.caption.fontWeight,
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            color: COLORS["ink-muted"],
          }}
        >
          {label}
        </label>
      )}
      <Tag
        rows={multiline ? rows : undefined}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className={`${className} ${uid}`}
        style={{
          width: "100%",
          backgroundColor: COLORS["surface-1"],
          border: `1px solid ${error ? COLORS.semantic.error : focused ? COLORS["accent-blue"] : COLORS.hairline}`,
          borderRadius: RADIUS.md,
          padding: `${SPACING.sm} ${SPACING.lg}`,
          fontSize: TYPOGRAPHY.body.fontSize,
          color: COLORS.ink,
          lineHeight: TYPOGRAPHY.body.lineHeight,
          letterSpacing: TYPOGRAPHY.body.letterSpacing,
          fontFamily: TYPOGRAPHY.fontFamily.body,
          outline: "none",
          transition: "border-color 0.2s ease, box-shadow 0.2s ease",
          boxShadow: error
            ? `0 0 0 1px ${COLORS.semantic.error}40`
            : focused
            ? SHADOWS.selected
            : "none",
          resize: multiline ? "none" : undefined,
          ...style,
        }}
        {...props}
      />
      {error && (
        <p style={{ fontSize: "12px", color: COLORS.semantic.error, margin: 0, display: "flex", alignItems: "center", gap: 6 }}>
          {error}
        </p>
      )}
    </div>
  );
}
