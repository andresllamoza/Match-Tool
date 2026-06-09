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
          yellow: "#FFC72C",
          "yellow-soft": "#FFF4D6",
          charcoal: "#111111",
          ink: "#1E242B",
          muted: "#6B6560",
          border: "#EAE5DC",
          green: "#1B7F4B",
          "green-soft": "#E8F5EE",
        },
      },
      fontFamily: {
        sans: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "16px",
        "2xl": "16px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 2px 12px rgba(17, 17, 17, 0.06)",
        "card-lg": "0 4px 24px rgba(17, 17, 17, 0.08)",
        sheet: "0 -8px 40px rgba(17, 17, 17, 0.12)",
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
      },
      animation: {
        "sheet-up": "sheet-up 0.32s cubic-bezier(0.32, 0.72, 0, 1)",
        "sheet-right": "sheet-right 0.28s cubic-bezier(0.32, 0.72, 0, 1)",
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
};
export default config;
