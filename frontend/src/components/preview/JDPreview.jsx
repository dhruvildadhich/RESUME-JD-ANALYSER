import React, { useState } from "react";
import { Card } from "../ui";
import PreviewModal from "./PreviewModal";
import HighlightedText from "./HighlightedText";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../../styles/designTokens";

export default function JDPreview({ jdText, matchedSkills = [], missingSkills = [] }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!jdText) return null;

  return (
    <>
      <Card
        variant="default"
        style={{
          display: "flex",
          flexDirection: "column",
          height: 400,
          padding: 0,
          overflow: "hidden",
          cursor: "pointer",
          transition: "transform 0.2s ease, border-color 0.2s ease",
        }}
        onClick={() => setIsModalOpen(true)}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = COLORS["accent-blue"];
          e.currentTarget.style.transform = "translateY(-2px)";
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = COLORS.hairline;
          e.currentTarget.style.transform = "none";
        }}
      >
        <div
          style={{
            padding: `${SPACING.sm} ${SPACING.md}`,
            borderBottom: `1px solid ${COLORS.hairline}`,
            backgroundColor: COLORS["surface-1"],
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: SPACING.sm }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["accent-blue"]} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <span style={{ fontSize: "13px", fontWeight: 600, color: COLORS.ink }}>
              Job Description
            </span>
          </div>
          <div
            style={{
              padding: "4px 8px",
              backgroundColor: `${COLORS["accent-blue"]}15`,
              color: COLORS["accent-blue"],
              borderRadius: RADIUS.sm,
              fontSize: "11px",
              fontWeight: 600,
            }}
          >
            Click to expand
          </div>
        </div>
        <div
          style={{
            flex: 1,
            padding: SPACING.md,
            overflowY: "auto",
            backgroundColor: COLORS.canvas,
            maskImage: "linear-gradient(to bottom, black 80%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to bottom, black 80%, transparent 100%)",
          }}
          className="custom-scrollbar"
        >
          <pre
            style={{
              margin: 0,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontFamily: TYPOGRAPHY.fontFamily.sans,
              fontSize: "13px",
              lineHeight: 1.6,
              color: COLORS["ink-muted"],
              pointerEvents: "none",
            }}
          >
            <HighlightedText text={jdText} matchedSkills={matchedSkills} missingSkills={missingSkills} />
          </pre>
        </div>
      </Card>

      <PreviewModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Job Description"
      >
        <div style={{ padding: SPACING.xl, height: "100%", overflowY: "auto" }} className="custom-scrollbar">
          <pre
            style={{
              margin: 0,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontFamily: TYPOGRAPHY.fontFamily.sans,
              fontSize: "14px",
              lineHeight: 1.7,
              color: COLORS.ink,
              maxWidth: 800,
              marginLeft: "auto",
              marginRight: "auto",
            }}
          >
            <HighlightedText text={jdText} matchedSkills={matchedSkills} missingSkills={missingSkills} />
          </pre>
        </div>
      </PreviewModal>
    </>
  );
}
