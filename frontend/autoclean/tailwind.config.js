/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  darkMode: 'class',
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        side:'#F4F7F9',
        main:'#004F6D',
        mainHover:'#00445e',


      },
    },
  },
  plugins: [],
};
