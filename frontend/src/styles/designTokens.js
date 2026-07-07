export const COLORS = {
  primary: "#ffffff",
  "on-primary": "#000000",
  "accent-blue": "#0099ff",
  ink: "#ffffff",
  "ink-muted": "#999999",
  canvas: "#090909",
  "surface-1": "#141414",
  "surface-2": "#1c1c1c",
  hairline: "#262626",
  "hairline-soft": "#1a1a1a",
  "inverse-canvas": "#ffffff",
  "inverse-ink": "#000000",
  "gradient-magenta": "#d44df0",
  "gradient-violet": "#6a4cf5",
  "gradient-orange": "#ff7a3d",
  "gradient-coral": "#ff5577",
  "primary-hover": "#e6e6e6",
  "surface-hover": "#2a2a2a",
  "semantic-success": "#22c55e",
  semantic: {
    success: "#22c55e",
    error: "#ef4444",
    warning: "#f59e0b",
    info: "#3b82f6",
  },
};

export const TYPOGRAPHY = {
  fontFamily: {
    display: "'GT Walsheim Medium', 'Mona Sans', 'Geist', Inter, system-ui, sans-serif",
    body: "'Inter Variable', Inter, system-ui, sans-serif",
  },
  displayXXL: { fontSize: "110px", fontWeight: 500, lineHeight: 0.85, letterSpacing: "-5.5px" },
  displayXL: { fontSize: "85px", fontWeight: 500, lineHeight: 0.95, letterSpacing: "-4.25px" },
  displayLG: { fontSize: "62px", fontWeight: 500, lineHeight: 1.0, letterSpacing: "-3.1px" },
  displayMD: { fontSize: "32px", fontWeight: 500, lineHeight: 1.13, letterSpacing: "-1.0px" },
  headline: { fontSize: "22px", fontWeight: 700, lineHeight: 1.2, letterSpacing: "-0.8px" },
  subhead: { fontSize: "24px", fontWeight: 400, lineHeight: 1.3, letterSpacing: "-0.01px" },
  bodyLG: { fontSize: "18px", fontWeight: 400, lineHeight: 1.3, letterSpacing: "-0.18px" },
  body: { fontSize: "15px", fontWeight: 400, lineHeight: 1.3, letterSpacing: "-0.15px" },
  bodySM: { fontSize: "14px", fontWeight: 500, lineHeight: 1.4, letterSpacing: "-0.14px" },
  caption: { fontSize: "13px", fontWeight: 500, lineHeight: 1.2, letterSpacing: "-0.13px" },
  micro: { fontSize: "12px", fontWeight: 400, lineHeight: 1.2, letterSpacing: "-0.12px" },
  button: { fontSize: "14px", fontWeight: 500, lineHeight: 1.0, letterSpacing: "-0.14px" },
};

export const SPACING = {
  hair: "1px",
  xxs: "4px",
  xs: "8px",
  sm: "12px",
  md: "15px",
  lg: "20px",
  xl: "30px",
  xxl: "40px",
  section: "96px",
};

export const RADIUS = {
  xs: "4px",
  sm: "6px",
  md: "10px",
  lg: "15px",
  xl: "20px",
  xxl: "30px",
  pill: "100px",
  full: "9999px",
};

export const SHADOWS = {
  none: "none",
  surface: "none",
  floating: "0px 10px 30px rgba(0,0,0,0.25), inset 0px 0.5px 0px rgba(255,255,255,0.10)",
  selected: "0px 0px 0px 1px rgba(0,153,255,0.15)",
};

export const ANIMATIONS = {
  duration: { fast: "150ms", normal: "300ms", slow: "500ms", xl: "1000ms" },
  easing: {
    default: "cubic-bezier(0.4,0,0.2,1)",
    spring: "cubic-bezier(0.22,1,0.36,1)",
    out: "cubic-bezier(0,0,0.2,1)",
  },
  hoverScale: "scale(1.02)",
  pressScale: "scale(0.97)",
  fade: { from: { opacity: 0 }, to: { opacity: 1 } },
};

export const BREAKPOINTS = {
  desktop: "1199px",
  tablet: "810px",
  mobileLg: "809px",
  mobileXs: "98px",
};
