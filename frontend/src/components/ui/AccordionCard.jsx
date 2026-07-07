import React, { useState, useRef, useEffect } from "react";
import { COLORS, SPACING, RADIUS } from "../../styles/designTokens";

/**
 * Reusable accordion card.
 * Summary row is always visible; detail body expands on click.
 *
 * Props:
 *   accentColor   – border/background tint  (e.g. COLORS["semantic-success"])
 *   summary       – JSX rendered in the collapsed header row
 *   children      – JSX rendered inside the expanded body
 *   defaultOpen   – boolean, open on mount (default false)
 *   id            – optional id for the wrapper div
 */
export default function AccordionCard({ accentColor, summary, children, defaultOpen = false, id }) {
  const [open, setOpen] = useState(defaultOpen);
  const bodyRef = useRef(null);
  const [bodyHeight, setBodyHeight] = useState(0);

  // Measure body height whenever children change or open state changes
  useEffect(() => {
    if (bodyRef.current) {
      setBodyHeight(bodyRef.current.scrollHeight);
    }
  }, [open, children]);

  return (
    <div
      id={id}
      onClick={() => setOpen((v) => !v)}
      style={{
        padding: `${SPACING.sm} ${SPACING.sm}`,
        borderRadius: RADIUS.lg,
        backgroundColor: `${accentColor}08`,
        border: `1px solid ${open ? `${accentColor}28` : `${accentColor}14`}`,
        cursor: "pointer",
        transition: "border-color 0.2s ease",
        userSelect: "none",
      }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = `${accentColor}28`; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = open ? `${accentColor}28` : `${accentColor}14`; }}
    >
      {/* ── Summary row (always visible) ─────────────────────────── */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
        <div style={{ flex: 1, minWidth: 0 }}>{summary}</div>
        {/* Chevron */}
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke={COLORS["ink-muted"]}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            flexShrink: 0,
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.25s ease",
          }}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      {/* ── Expanding body ────────────────────────────────────────── */}
      <div
        style={{
          overflow: "hidden",
          maxHeight: open ? `${bodyHeight}px` : "0px",
          transition: "max-height 0.28s cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        <div
          ref={bodyRef}
          onClick={(e) => e.stopPropagation()} // prevent collapse when clicking links inside
          style={{ paddingTop: SPACING.sm }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
