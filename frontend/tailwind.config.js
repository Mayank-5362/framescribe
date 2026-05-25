/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"] ,
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 30px rgba(56, 189, 248, 0.25)",
      },
    },
  },
  plugins: [],
};
