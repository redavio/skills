/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  // Follows the visitor's system setting. (An app that toggles dark mode with a class can reuse
  // the same components with darkMode: "class".)
  darkMode: "media",
  theme: {
    extend: {
      // Your brand color, set in src/index.css.
      colors: { brand: "rgb(var(--brand) / <alpha-value>)" },
    },
  },
  plugins: [],
};
