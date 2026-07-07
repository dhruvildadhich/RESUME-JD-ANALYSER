import React, { useCallback, useRef, useState } from "react";
import { Card, Button } from "./ui";
import { COLORS, RADIUS, SPACING, TYPOGRAPHY } from "../styles/designTokens";

export default function UploadForm({ onSubmit, isLoading }) {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [fileError, setFileError] = useState("");
  const fileInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    setFileError("");
    if (!file) return;
    if (file.type !== "application/pdf") {
      setFileError("Only PDF files are accepted.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setFileError("File must be smaller than 10 MB.");
      return;
    }
    setResumeFile(file);
  }, []);

  const onFileInput = (e) => handleFile(e.target.files[0]);
  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!resumeFile || !jdText.trim()) return;
    onSubmit(resumeFile, jdText.trim());
  };

  const canSubmit = resumeFile && jdText.trim().length >= 50 && !isLoading;

  return (
    <form onSubmit={handleSubmit} id="analyze-form">
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: SPACING.xl,
        }}
        className="max-md:grid-cols-1"
      >
        <Card variant="default">
          <div style={{ display: "flex", flexDirection: "column", gap: SPACING.md }}>
            <div style={{ display: "flex", alignItems: "center", gap: SPACING.xs }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["ink-muted"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              <span
                style={{
                  fontSize: TYPOGRAPHY.caption.fontSize,
                  fontWeight: TYPOGRAPHY.caption.fontWeight,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: COLORS["ink-muted"],
                }}
              >
                Resume Upload
              </span>
            </div>

            <div
              id="resume-drop-zone"
              role="button"
              tabIndex={0}
              aria-label="Upload resume PDF. Click or drag and drop."
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInputRef.current?.click(); } }}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: SPACING.md,
                padding: `${SPACING.xl} ${SPACING.lg}`,
                borderRadius: RADIUS.lg,
                border: `2px dashed ${isDragging ? COLORS["accent-blue"] : resumeFile ? `${COLORS["semantic-success"]}59` : COLORS.hairline}`,
                backgroundColor: isDragging ? `${COLORS["accent-blue"]}0d` : resumeFile ? `${COLORS["semantic-success"]}08` : "transparent",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              <input
                ref={fileInputRef}
                id="resume-file-input"
                type="file"
                accept=".pdf,application/pdf"
                onChange={onFileInput}
                className="hidden"
              />

              {resumeFile ? (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: SPACING.sm, textAlign: "center" }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={COLORS["semantic-success"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  <div>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: COLORS["semantic-success"], margin: 0 }}>{resumeFile.name}</p>
                    <p style={{ fontSize: "11px", color: COLORS["ink-muted"], margin: "4px 0 0" }}>{(resumeFile.size / 1024).toFixed(1)} KB — Click to change</p>
                  </div>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: SPACING.sm, textAlign: "center" }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={COLORS["ink-muted"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  <div>
                    <p style={{ fontSize: "13px", color: COLORS["ink-muted"], margin: 0 }}>
                      Drop your resume here or <span style={{ color: COLORS["ink"], fontWeight: 600 }}>browse</span>
                    </p>
                    <p style={{ fontSize: "11px", color: COLORS["ink-muted"], margin: "4px 0 0", opacity: 0.6 }}>PDF only — Max 10 MB</p>
                  </div>
                </div>
              )}
            </div>
            {fileError && (
              <p style={{ fontSize: "12px", color: COLORS.semantic.error, margin: 0, display: "flex", alignItems: "center", gap: 6 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                {fileError}
              </p>
            )}
          </div>
        </Card>

        <Card variant="default">
          <div style={{ display: "flex", flexDirection: "column", gap: SPACING.sm }}>
            <div style={{ display: "flex", alignItems: "center", gap: SPACING.xs }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={COLORS["ink-muted"]} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
              <span
                style={{
                  fontSize: TYPOGRAPHY.caption.fontSize,
                  fontWeight: TYPOGRAPHY.caption.fontWeight,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: COLORS["ink-muted"],
                }}
              >
                Job Description
              </span>
            </div>

            <textarea
              id="jd-textarea"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the full job description here..."
              rows={8}
              style={{
                width: "100%",
                backgroundColor: COLORS["surface-2"],
                border: `1px solid ${COLORS.hairline}`,
                borderRadius: RADIUS.md,
                padding: `${SPACING.sm} ${SPACING.lg}`,
                fontSize: TYPOGRAPHY.bodySM.fontSize,
                color: COLORS.ink,
                lineHeight: 1.6,
                fontFamily: TYPOGRAPHY.fontFamily.body,
                outline: "none",
                resize: "none",
                transition: "border-color 0.2s ease",
              }}
              onFocus={(e) => (e.target.style.borderColor = COLORS["accent-blue"])}
              onBlur={(e) => (e.target.style.borderColor = COLORS.hairline)}
            />
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <span
                style={{
                  fontSize: "11px",
                  color: jdText.length < 50 ? COLORS["ink-muted"] : COLORS["semantic-success"],
                  opacity: jdText.length < 50 ? 0.6 : 1,
                  transition: "color 0.2s ease",
                }}
              >
                {jdText.length} characters {jdText.length < 50 ? "(min 50)" : "✓"}
              </span>
            </div>
          </div>
        </Card>
      </div>

      <div style={{ display: "flex", justifyContent: "center", marginTop: SPACING.xl }}>
        <Button
          id="analyze-btn"
          type="submit"
          disabled={!canSubmit}
          variant="primary"
          style={{ padding: "14px 40px", fontSize: "15px" }}
        >
          {isLoading ? (
            <>
              <svg className="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <circle cx="12" cy="12" r="10" opacity="0.25" />
                <path d="M12 2a10 10 0 019.95 9" />
              </svg>
              Analyzing...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              Analyze Candidate Match
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
