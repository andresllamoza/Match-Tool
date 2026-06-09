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
        cream: {
          DEFAULT: "#FBF6EC",
          dark: "#F3EBD9",
          deeper: "#EBE0C8",
        },
        bee: {
          blue: "#1B4F9C",
          "blue-hover": "#163F7D",
          "blue-light": "#E8F0FA",
          yellow: "#F5C518",
          ink: "#1A1A1A",
          muted: "#5C5C5C",
          border: "#E5D9C3",
        },
      },
      fontFamily: {
        sans: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "16px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 4px 24px rgba(27, 79, 156, 0.08)",
        "card-lg": "0 8px 40px rgba(27, 79, 156, 0.12)",
      },
      maxWidth: {
        journey: "28rem",
        desktop: "72rem",
      },
    },
  },
  plugins: [],
};
export default config;
