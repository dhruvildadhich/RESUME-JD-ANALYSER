import React from "react";
import { COLORS, RADIUS, SPACING, SHADOWS } from "../../styles/designTokens";

const variants = {
  default: {
    bg: COLORS["surface-1"],
    border: "none",
    shadow: SHADOWS.none,
  },
  featured: {
    bg: COLORS["surface-2"],
    border: "none",
    shadow: SHADOWS.floating,
  },
  gradient: {
    bg: COLORS["gradient-violet"],
    border: "none",
    shadow: SHADOWS.none,
    color: COLORS.ink,
  },
  glass: {
    bg: `${COLORS["surface-1"]}cc`,
    border: `1px solid ${COLORS.hairline}66`,
    shadow: SHADOWS.none,
    backdrop: "blur(16px)",
  },
};

export default function Card({ variant = "default", padding, children, className = "", style, ...props }) {
  const cfg = variants[variant] || variants.default;

  return (
    <div
      className={className}
      style={{
        backgroundColor: cfg.bg,
        color: cfg.color || COLORS.ink,
        borderRadius: RADIUS.xl,
        padding: padding || SPACING.xl,
        border: cfg.border || "none",
        boxShadow: cfg.shadow,
        WebkitBackdropFilter: cfg.backdrop,
        backdropFilter: cfg.backdrop,
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}
