/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        koreum: {
          50: "#eef4ff",
          100: "#d9e6ff",
          200: "#bcd3ff",
          300: "#8eb5ff",
          400: "#598dff",
          500: "#3366ff",
          600: "#1f48f5",
          700: "#1736db",
          800: "#172eb0",
          900: "#192b8a",
        },
      },
    },
  },
  plugins: [],
};
