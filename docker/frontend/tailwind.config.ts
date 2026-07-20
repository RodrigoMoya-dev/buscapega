import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Paleta oficial de Buscapega (grafica/palette.scss). Habilita utilidades como
      // text-marca-pino, bg-marca-naranja o border-marca-celadon.
      colors: {
        marca: {
          celadon: "#bcd8c1",
          pino: "#297373",
          naranja: "#c84c09",
          bordeaux: "#420217",
          blush: "#fad8d6",
        },
      },
    },
  },
  plugins: [],
};

export default config;
