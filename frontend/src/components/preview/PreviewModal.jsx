import React, { useEffect } from "react";
import { COLORS, RADIUS, SPACING } from "../../styles/designTokens";

export default function PreviewModal({ isOpen, onClose, title, children }) {
  // Handle ESC key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent background scrolling
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: SPACING.xl,
        backgroundColor: "rgba(0, 0, 0, 0.6)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        animation: "fadeIn 0.2s ease",
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 1000,
          height: "90vh",
          backgroundColor: COLORS.canvas,
          borderRadius: RADIUS.lg,
          border: `1px solid ${COLORS.hairline}`,
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          animation: "slideUp 0.3s cubic-bezier(0.22, 1, 0.36, 1)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            padding: `${SPACING.md} ${SPACING.xl}`,
            borderBottom: `1px solid ${COLORS.hairline}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            backgroundColor: COLORS["surface-1"],
          }}
        >
          <h2 style={{ fontSize: "18px", fontWeight: 600, color: COLORS.ink, margin: 0 }}>
            {title}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: COLORS["ink-muted"],
              cursor: "pointer",
              padding: SPACING.xs,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: RADIUS.md,
              transition: "background 0.2s ease, color 0.2s ease",
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = COLORS["surface-2"];
              e.currentTarget.style.color = COLORS.ink;
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "transparent";
              e.currentTarget.style.color = COLORS["ink-muted"];
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div style={{ flex: 1, overflow: "hidden", position: "relative" }}>
          {children}
        </div>
      </div>
    </div>
  );
}
