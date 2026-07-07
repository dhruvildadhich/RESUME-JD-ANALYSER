/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Inter Variable'", "Inter", "system-ui", "sans-serif"],
        display: ["'GT Walsheim Medium'", "'Mona Sans'", "Geist", "Inter", "system-ui", "sans-serif"],
      },
      colors: {
        canvas: "#090909",
        "surface-1": "#141414",
        "surface-2": "#1c1c1c",
        "ink": "#ffffff",
        "ink-muted": "#999999",
        "accent-blue": "#0099ff",
        "hairline": "#262626",
        "hairline-soft": "#1a1a1a",
      },
      animation: {
        "spin-slow": "spin 3s linear infinite",
        "fade-in": "fadeIn 0.5s cubic-bezier(0.22, 1, 0.36, 1)",
        "slide-up": "slideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1)",
        "slide-down": "slideDown 0.3s cubic-bezier(0.22, 1, 0.36, 1)",
        "scale-in": "scaleIn 0.3s cubic-bezier(0.22, 1, 0.36, 1)",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(99, 102, 241, 0.4)" },
          "50%": { boxShadow: "0 0 20px 8px rgba(99, 102, 241, 0.15)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
    },
  },
  plugins: [],
};
