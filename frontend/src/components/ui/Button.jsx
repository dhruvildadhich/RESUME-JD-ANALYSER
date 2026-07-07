import React from "react";
import { COLORS, RADIUS, TYPOGRAPHY, SPACING } from "../../styles/designTokens";

const variants = {
  primary: { bg: COLORS.primary, color: COLORS["on-primary"], hover: COLORS["primary-hover"] },
  secondary: { bg: COLORS["surface-1"], color: COLORS.ink, hover: COLORS["surface-2"], border: COLORS.hairline },
  translucent: { bg: COLORS["surface-2"], color: COLORS.ink, hover: COLORS["surface-hover"] },
  icon: { bg: COLORS["surface-1"], color: COLORS.ink, hover: COLORS["surface-2"], border: COLORS.hairline },
};

export default function Button({ variant = "primary", children, className = "", style, ...props }) {
  const [hovered, setHovered] = React.useState(false);
  const cfg = variants[variant] || variants.primary;

  return (
    <button
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={`inline-flex items-center justify-center gap-2 transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100
        active:scale-[0.97] ${variant === "icon" ? "w-10 h-10 p-0" : ""} ${className}`}
      style={{
        backgroundColor: hovered ? cfg.hover : cfg.bg,
        color: cfg.color,
        borderRadius: RADIUS.pill,
        padding: variant === "icon" ? 0 : `${SPACING.sm} ${SPACING.lg}`,
        fontSize: TYPOGRAPHY.button.fontSize,
        fontWeight: TYPOGRAPHY.button.fontWeight,
        lineHeight: TYPOGRAPHY.button.lineHeight,
        letterSpacing: TYPOGRAPHY.button.letterSpacing,
        border: cfg.border ? `1px solid ${cfg.border}` : "none",
        fontFamily: TYPOGRAPHY.fontFamily.body,
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  );
}
