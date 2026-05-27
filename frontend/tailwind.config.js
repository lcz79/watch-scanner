/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:      ['Space Grotesk', 'system-ui', 'sans-serif'],
        display:   ['Space Grotesk', 'system-ui', 'sans-serif'],
        serif:     ['"Playfair Display"', 'Georgia', 'serif'],
        cormorant: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        mono:      ['"IBM Plex Mono"', 'Menlo', 'monospace'],
      },
      colors: {
        navy: {
          DEFAULT: '#07080f',
          2:  '#0c0e1a',
          3:  '#111425',
          4:  '#161928',
        },
        gold: {
          DEFAULT: '#B8975A',
          dim:    'rgba(184,151,90,0.15)',
          glow:   'rgba(184,151,90,0.25)',
          300: '#d4b07a',
          400: '#B8975A',
          500: '#9a7c45',
        },
        signal: {
          green: '#4EB87A',
          red:   '#E05A5A',
          blue:  '#8899ff',
        },
        text: {
          1: '#e8e2d4',
          2: '#8a8070',
          3: '#3d3a30',
        },
        // Keep zinc for backward compat
        zinc: {
          50:  '#fafafa',
          100: '#f4f4f5',
          200: '#e4e4e7',
          300: '#d4d4d8',
          400: '#a1a1aa',
          500: '#71717a',
          600: '#52525b',
          700: '#3f3f46',
          800: '#27272a',
          850: '#1e1e22',
          900: '#18181b',
          950: '#09090b',
        },
        // Keep yellow for backward compat
        yellow: {
          400: '#B8975A',
          500: '#9a7c45',
        },
        // Keep primary for backward compat
        primary:      '#B8975A',
        'on-primary': '#07080f',
      },
      borderRadius: {
        DEFAULT: '2px',
        sm: '1px',
        md: '4px',
        lg: '6px',
        xl: '8px',
        full: '9999px',
      },
      boxShadow: {
        gold:     '0 0 20px rgba(184,151,90,0.2)',
        'gold-lg':'0 0 40px rgba(184,151,90,0.15), 0 0 80px rgba(184,151,90,0.05)',
        card:     '0 2px 16px rgba(0,0,0,0.4)',
        'card-hover': '0 8px 40px rgba(0,0,0,0.6), 0 0 30px rgba(184,151,90,0.1)',
      },
    },
  },
  plugins: [],
}
