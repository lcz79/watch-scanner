/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Satoshi', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Cabinet Grotesk', 'system-ui', 'sans-serif'],
      },
      colors: {
        gold: {
          400: '#D4A82A',
          500: '#C49A20',
          600: '#A8830F',
        },
      },
    },
  },
  plugins: [],
}
