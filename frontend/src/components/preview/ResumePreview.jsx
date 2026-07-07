import React, { useState, useEffect } from "react";
import { Card } from "../ui";
import PreviewModal from "./PreviewModal";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../../styles/designTokens";

export default function ResumePreview({ resumeFile }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [objectUrl, setObjectUrl] = useState(null);

  useEffect(() => {
    if (resumeFile) {
      const url = URL.createObjectURL(resumeFile);
      setObjectUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [resumeFile]);

  if (!resumeFile) return null;

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
          position: "relative",
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
            </svg>
            <span style={{ fontSize: "13px", fontWeight: 600, color: COLORS.ink, textOverflow: "ellipsis", whiteSpace: "nowrap", overflow: "hidden", maxWidth: 200 }}>
              {resumeFile.name}
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
        <div style={{ flex: 1, position: "relative", overflow: "hidden", pointerEvents: "none" }}>
          {objectUrl ? (
            <object
              data={`${objectUrl}#toolbar=0&navpanes=0&scrollbar=0`}
              type="application/pdf"
              style={{ width: "100%", height: "100%", opacity: 0.9 }}
            >
              Preview not available.
            </object>
          ) : (
            <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: COLORS["ink-muted"] }}>
              Loading preview...
            </div>
          )}
          <div style={{ position: "absolute", inset: 0, zIndex: 10, background: "transparent" }}></div>
        </div>
      </Card>

      <PreviewModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={resumeFile.name}
      >
        {objectUrl && (
          <iframe
            src={`${objectUrl}#toolbar=1`}
            style={{ width: "100%", height: "100%", border: "none" }}
            title="Resume Preview"
          />
        )}
      </PreviewModal>
    </>
  );
}
