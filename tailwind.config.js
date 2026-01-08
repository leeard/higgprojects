/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html", "./src/**/*.js"],
  theme: {
    extend: {
      fontFamily: {
        'display': ['"Bebas Neue"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        higgprojects: {
          "primary": "#5EEAD4",
          "secondary": "#2DD4BF",
          "accent": "#F0FDFA",
          "neutral": "#1f2937",
          "base-100": "#0a0a0a",
          "base-200": "#141414",
          "base-300": "#1f1f1f",
          "info": "#22D3EE",
          "success": "#34D399",
          "warning": "#FBBF24",
          "error": "#F87171",
        },
      },
      "dark",
      "light",
    ],
  },
}
