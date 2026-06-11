import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#FAF8F5",
          alt: "#F9F3E6",
        },
        cream: {
          DEFAULT: "#FAF8F5",
          dark: "#F3EDE4",
          deeper: "#EAE5DC",
        },
        bee: {
          yellow: "#F5BE17",
          "yellow-hover": "#E0AB10",
          "yellow-soft": "#FFF4D6",
          "yellow-tint": "#FFF9E6",
          charcoal: "#111111",
          ink: "#1E242B",
          muted: "#5A554E",
          faint: "#8A857B",
          border: "#EAE5DC",
          "border-strong": "#D9D2C8",
          green: "#1B7F4B",
          "green-soft": "#E8F5EE",
          gold: "#8A5A00",
          pink: "#F5D0D8",
        },
      },
      fontFamily: {
        sans: ["var(--font-mulish)", "system-ui", "sans-serif"],
        display: ["var(--font-mulish)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        input: "12px",
        cta: "12px",
        block: "14px",
        card: "16px",
        "2xl": "16px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 2px 12px rgba(17, 17, 17, 0.06)",
        "card-lg": "0 4px 24px rgba(17, 17, 17, 0.08)",
        sheet: "0 -8px 40px rgba(17, 17, 17, 0.12)",
        "cta-glow": "0 4px 20px rgba(245, 190, 23, 0.35)",
      },
      maxWidth: {
        journey: "28rem",
        desktop: "72rem",
      },
      keyframes: {
        "sheet-up": {
          "0%": { transform: "translateY(100%)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "sheet-right": {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shake: {
          "0%, 100%": { transform: "translateX(0)" },
          "20%": { transform: "translateX(-6px)" },
          "40%": { transform: "translateX(6px)" },
          "60%": { transform: "translateX(-4px)" },
          "80%": { transform: "translateX(4px)" },
        },
        "toast-up": {
          "0%": { transform: "translateY(110%)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "pulse-border": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(245, 190, 23, 0.45)" },
          "50%": { boxShadow: "0 0 0 4px rgba(245, 190, 23, 0.25)" },
        },
        fluidWandering: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
      animation: {
        "sheet-up": "sheet-up 0.32s cubic-bezier(0.32, 0.72, 0, 1)",
        "sheet-right": "sheet-right 0.28s cubic-bezier(0.32, 0.72, 0, 1)",
        "fade-in": "fade-in 0.2s ease-out",
        shake: "shake 0.45s ease-in-out",
        "toast-up": "toast-up 0.38s cubic-bezier(0.32, 0.72, 0, 1)",
        "pulse-border": "pulse-border 2.4s ease-in-out infinite",
        fluidWandering: "fluidWandering 15s ease infinite",
      },
    },
  },
  plugins: [],
};
export default config;
