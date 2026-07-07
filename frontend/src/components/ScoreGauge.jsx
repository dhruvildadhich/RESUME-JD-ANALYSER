import React from "react";
import { COLORS, TYPOGRAPHY, RADIUS, SPACING } from "../styles/designTokens";

export default function ScoreGauge({ score }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const segments = [
    { range: [0, 40], color: COLORS.semantic.error, label: "Not Recommended" },
    { range: [40, 70], color: COLORS.semantic.warning, label: "Potential Match" },
    { range: [70, 100], color: COLORS["semantic-success"], label: "Strong Match" },
  ];
  const active = segments.find((s) => clamped >= s.range[0] && clamped < s.range[1]) || segments[segments.length - 1];

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: SPACING.md }}>
      <span
        style={{
          fontSize: "64px",
          fontWeight: 800,
          lineHeight: 1,
          letterSpacing: "-3px",
          color: active.color,
          fontFamily: TYPOGRAPHY.fontFamily.display,
        }}
      >
        {clamped}
        <span style={{ fontSize: "24px", fontWeight: 500, color: COLORS["ink-muted"], letterSpacing: "-1px" }}>
          /100
        </span>
      </span>
      <div
        style={{
          width: "100%",
          height: 4,
          backgroundColor: COLORS["surface-2"],
          borderRadius: RADIUS.full,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${clamped}%`,
            height: "100%",
            backgroundColor: active.color,
            borderRadius: RADIUS.full,
            transition: "width 1s cubic-bezier(0.22, 1, 0.36, 1)",
          }}
        />
      </div>
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          padding: "6px 14px",
          borderRadius: RADIUS.pill,
          fontSize: "12px",
          fontWeight: 700,
          letterSpacing: "-0.12px",
          backgroundColor: `${active.color}18`,
          color: active.color,
          border: `1px solid ${active.color}30`,
        }}
      >
        {active.label}
      </span>
    </div>
  );
}
