module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "#2D3748",
        input: "#2D3748",
        ring: "#667EEA",
        background: "#0A0E27",
        foreground: "#F7FAFC",
        primary: {
          DEFAULT: "#667EEA",
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#764BA2",
          foreground: "#FFFFFF",
        },
        destructive: {
          DEFAULT: "#F56565",
          foreground: "#FFFFFF",
        },
        muted: {
          DEFAULT: "#1A202C",
          foreground: "#A0AEC0",
        },
        accent: {
          DEFAULT: "#48BB78",
          foreground: "#FFFFFF",
        },
        popover: {
          DEFAULT: "#1A202C",
          foreground: "#F7FAFC",
        },
        card: {
          DEFAULT: "rgba(26, 32, 44, 0.6)",
          foreground: "#F7FAFC",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["Poppins", "sans-serif"],
        mono: ['"Roboto Mono"', "monospace"],
      },
      fontSize: {
        h1: "48px",
        h2: "36px",
        h3: "28px",
        body: "16px",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        wave: {
          "0%, 100%": { transform: "scaleY(1)" },
          "50%": { transform: "scaleY(1.5)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        wave: "wave 1.2s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
      },
      boxShadow: {
        'neon': '0 0 20px rgba(102, 126, 234, 0.5), 0 0 40px rgba(102, 126, 234, 0.3)',
        'neon-strong': '0 0 30px rgba(102, 126, 234, 0.7), 0 0 60px rgba(102, 126, 234, 0.5)',
      },
    },
  },
  plugins: [],
};
