import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        giver: {
          ink: "#0f172a",
          slate: "#334155",
          mist: "#f1f5f9",
          accent: "#2563eb",
          warn: "#b45309",
          ok: "#15803d",
          low: "#64748b",
        },
      },
    },
  },
  plugins: [],
};

export default config;
