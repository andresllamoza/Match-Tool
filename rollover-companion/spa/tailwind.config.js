/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#FAF8F5",
        ink: "#111111",
        "ink-hover": "#2b2b2b",
        bee: "#FFC72C",
        muted: "#8A857B",
        border: "#EEE9DF",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(17, 17, 17, 0.04)",
      },
      maxWidth: {
        customer: "480px",
      },
    },
  },
  plugins: [],
};
