import React, { useState, useEffect, Component } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Brain, Search, Network, Bot, Check, AlertCircle, RefreshCw } from 'lucide-react';
import { COLORS, SPACING, RADIUS, TYPOGRAPHY } from '../../styles/designTokens';

// ── Resolved token aliases (guards against missing paths) ────────────────────
const ink        = COLORS.ink;
const inkMuted   = COLORS["ink-muted"];
const hairline   = COLORS.hairline;
const danger     = COLORS.semantic?.error ?? "#ef4444";
const primary    = COLORS.primary;
const canvas     = COLORS.canvas;
const fontBody   = TYPOGRAPHY.fontFamily?.body ?? "Inter, system-ui, sans-serif";
const fontMD     = TYPOGRAPHY.bodySM?.fontSize ?? "14px";
const fontSM     = TYPOGRAPHY.caption?.fontSize ?? "13px";
const spacingXL  = SPACING.xl;
const spacingXXL = SPACING.xxl;
const spacingMD  = SPACING.md;
const spacingSM  = SPACING.sm;
const spacingXS  = SPACING.xs;
const radiusLG   = RADIUS.lg;
const radiusMD   = RADIUS.md;

// ── Steps ────────────────────────────────────────────────────────────────────
const STEPS = [
  {
    id: 1, delay: 0,
    title: 'Reading Resume',
    desc: 'Parsing candidate profile, extracting experience, projects, and education',
    icon: FileText,
  },
  {
    id: 2, delay: 2000,
    title: 'Understanding Candidate Profile',
    desc: 'Identifying technical competencies, seniority signals, and evidence depth',
    icon: Brain,
  },
  {
    id: 3, delay: 5000,
    title: 'Analyzing Job Requirements',
    desc: 'Mapping required skills, responsibilities, and must-have qualifications',
    icon: Search,
  },
  {
    id: 4, delay: 8000,
    title: 'Evaluating Skill Alignment',
    desc: 'Measuring fit across critical, important, and optional role requirements',
    icon: Network,
  },
  {
    id: 5, delay: 12000,
    title: 'Generating Recruiter Report',
    desc: 'Preparing match score, evidence-backed insights, and improvement recommendations',
    icon: Bot,
  },
];

const STATUS_MESSAGES = [
  "Reading candidate profile...",
  "Evaluating experience depth...",
  "Mapping job requirements...",
  "Assessing skill alignment...",
  "Preparing recruiter insights...",
];

// ── Error Boundary ────────────────────────────────────────────────────────────
export class AnalysisErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("[AnalysisErrorBoundary]", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: spacingXXL,
            borderRadius: radiusLG,
            border: `1px solid ${danger}25`,
            backgroundColor: `${danger}08`,
            textAlign: "center",
            maxWidth: 600,
            margin: "0 auto",
          }}
        >
          <AlertCircle size={32} color={danger} style={{ marginBottom: spacingSM }} />
          <h3 style={{ color: ink, fontWeight: 700, fontSize: "16px", margin: `0 0 ${spacingSM}`, fontFamily: fontBody }}>
            Something went wrong
          </h3>
          <p style={{ color: inkMuted, fontSize: fontSM, margin: `0 0 ${spacingMD}`, lineHeight: 1.5, fontFamily: fontBody }}>
            An unexpected error occurred while displaying the analysis.
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              background: "rgba(255,255,255,0.08)",
              border: `1px solid rgba(255,255,255,0.15)`,
              color: ink,
              padding: "8px 16px",
              borderRadius: radiusMD,
              cursor: "pointer",
              fontWeight: 500,
              fontSize: fontSM,
              fontFamily: fontBody,
            }}
          >
            <RefreshCw size={14} />
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function AIAnalysisProgress({ isApiComplete, isError, errorMessage, onComplete, onRetry }) {
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [statusMessageIndex, setStatusMessageIndex] = useState(0);

  // Status message rotation
  useEffect(() => {
    if (isApiComplete || isError) return;
    const interval = setInterval(() => {
      setStatusMessageIndex((prev) => (prev + 1) % STATUS_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [isApiComplete, isError]);

  // Step advancement
  useEffect(() => {
    if (isError) return;

    if (isApiComplete) {
      setActiveStepIndex(STEPS.length);
      const timeout = setTimeout(() => {
        if (onComplete) onComplete();
      }, 800);
      return () => clearTimeout(timeout);
    }

    const timeouts = STEPS.map((step, index) => {
      if (index === 0) return null;
      return setTimeout(() => {
        if (!isApiComplete && !isError) {
          setActiveStepIndex(index);
        }
      }, step.delay);
    });

    return () => timeouts.forEach((t) => t && clearTimeout(t));
  }, [isApiComplete, isError, onComplete]);

  return (
    <div
      style={{
        background: 'rgba(255,255,255,0.04)',
        border: `1px solid rgba(255,255,255,0.1)`,
        borderRadius: radiusLG,
        padding: spacingXXL,
        maxWidth: 800,
        margin: '0 auto',
        width: '100%',
        color: ink,
        fontFamily: fontBody,
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: spacingXL, textAlign: 'center' }}>
        <h2 style={{ fontWeight: 600, marginBottom: spacingXS, color: ink, fontSize: "18px", fontFamily: fontBody }}>
          {isError ? 'Analysis Failed' : 'AI Analysis in Progress'}
        </h2>
        <div style={{ height: 24, overflow: 'hidden' }}>
          <AnimatePresence mode="wait">
            {!isError ? (
              <motion.p
                key={statusMessageIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                style={{ color: inkMuted, fontSize: fontSM, margin: 0, fontFamily: fontBody }}
              >
                {activeStepIndex === STEPS.length - 1 && !isApiComplete
                  ? "Finalizing candidate evaluation..."
                  : STATUS_MESSAGES[statusMessageIndex]}
              </motion.p>
            ) : (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ color: danger, fontSize: fontSM, margin: 0, fontFamily: fontBody }}
              >
                {errorMessage || "An unexpected error occurred."}
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Steps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacingMD }}>
        {STEPS.map((step, index) => {
          const isCompleted = index < activeStepIndex || (isApiComplete && index <= activeStepIndex);
          const isActive    = index === activeStepIndex && !isApiComplete && !isError;
          const isPending   = index > activeStepIndex && !isError;
          const Icon        = step.icon;

          return (
            <div
              key={step.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: spacingMD,
                opacity: isPending ? 0.4 : 1,
                transition: 'opacity 0.3s',
              }}
            >
              {/* Step indicator */}
              <div style={{ position: 'relative', marginTop: 4 }}>
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    style={{
                      width: 28, height: 28, borderRadius: '50%', background: primary,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                  >
                    <Check size={16} color={canvas} strokeWidth={3} />
                  </motion.div>
                ) : isActive ? (
                  <motion.div
                    animate={{ boxShadow: [`0 0 0 0 rgba(255,255,255,0.2)`, `0 0 0 10px rgba(255,255,255,0)`] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    style={{
                      width: 28, height: 28, borderRadius: '50%', border: `2px solid ${primary}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: 'rgba(255,255,255,0.1)',
                    }}
                  >
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: primary }} />
                  </motion.div>
                ) : (
                  <div
                    style={{
                      width: 28, height: 28, borderRadius: '50%', border: `2px solid ${hairline}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                  />
                )}

                {/* Connecting line */}
                {index < STEPS.length - 1 && (
                  <div
                    style={{
                      position: 'absolute', top: 28, left: 13, width: 2, height: 32,
                      background: isCompleted ? primary : hairline,
                      transition: 'background 0.3s',
                    }}
                  />
                )}
              </div>

              {/* Label */}
              <div style={{ paddingBottom: index < STEPS.length - 1 ? 16 : 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: spacingSM }}>
                  <Icon size={18} color={isCompleted || isActive ? primary : inkMuted} />
                  <h3
                    style={{
                      fontSize: fontMD,
                      fontWeight: 500,
                      margin: 0,
                      color: isCompleted || isActive ? ink : inkMuted,
                      fontFamily: fontBody,
                    }}
                  >
                    {step.title}
                  </h3>
                </div>
                <p
                  style={{
                    margin: '4px 0 0 0',
                    fontSize: fontSM,
                    color: inkMuted,
                    paddingLeft: 26,
                    fontFamily: fontBody,
                    lineHeight: 1.5,
                  }}
                >
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Retry button */}
      {isError && onRetry && (
        <div style={{ marginTop: spacingXL, display: 'flex', justifyContent: 'center' }}>
          <button
            onClick={onRetry}
            style={{
              display: 'flex', alignItems: 'center', gap: 8,
              background: 'rgba(255,255,255,0.1)', border: `1px solid rgba(255,255,255,0.2)`,
              color: ink, padding: '8px 16px', borderRadius: radiusMD, cursor: 'pointer',
              fontWeight: 500, fontFamily: fontBody, fontSize: fontSM,
            }}
            onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.2)'; }}
            onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; }}
          >
            <AlertCircle size={16} />
            Retry Analysis
          </button>
        </div>
      )}
    </div>
  );
}
