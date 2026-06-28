import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1e3a5f",
          50: "#e8f0fb",
          100: "#c5d6f4",
          200: "#9db8eb",
          300: "#7099e2",
          400: "#4e80db",
          500: "#2c67d4",
          600: "#1e3a5f",
          700: "#162c48",
          800: "#0e1d31",
          900: "#060f1a",
        },
        accent: "#e74c3c",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
