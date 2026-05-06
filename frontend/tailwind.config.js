/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      // ── Font families (exact Stitch definitions) ───────────────────────────
      fontFamily: {
        'display-price': ['Space Grotesk'],
        'h1':            ['Space Grotesk'],
        'h2':            ['Space Grotesk'],
        'mono-data':     ['Space Grotesk'],
        'body-md':       ['Inter'],
        'body-lg':       ['Inter'],
        'label-caps':    ['Inter'],
        // Convenience aliases
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
      },

      // ── Font sizes (exact Stitch definitions) ──────────────────────────────
      fontSize: {
        'display-price': ['48px', { lineHeight: '1.1',  letterSpacing: '-0.02em', fontWeight: '700' }],
        'h1':            ['32px', { lineHeight: '1.2',  fontWeight: '600' }],
        'h2':            ['24px', { lineHeight: '1.3',  fontWeight: '600' }],
        'body-lg':       ['18px', { lineHeight: '1.6',  fontWeight: '400' }],
        'body-md':       ['16px', { lineHeight: '1.5',  fontWeight: '400' }],
        'mono-data':     ['14px', { lineHeight: '1',    fontWeight: '500' }],
        'label-caps':    ['12px', { lineHeight: '1',    letterSpacing: '0.05em', fontWeight: '600' }],
      },

      // ── Colors (Stitch MD3 tokens — do NOT override zinc) ─────────────────
      colors: {
        // MD3 primary / gold
        primary:             '#f2c345',
        'on-primary':        '#3e2e00',
        'primary-container': '#d4a82a',
        'primary-fixed':     '#ffdf95',
        'primary-fixed-dim': '#efc142',

        // MD3 secondary
        secondary:                '#c8c5ca',
        'on-secondary':           '#303033',
        'secondary-container':    '#47464a',
        'on-secondary-container': '#b6b4b8',

        // MD3 tertiary
        tertiary:             '#b3c9ff',
        'on-tertiary':        '#002e6b',
        'tertiary-container': '#87adff',

        // MD3 surface (warm sepia scale — used as separate tokens)
        surface:                     '#17130b',
        'surface-dim':               '#17130b',
        'surface-bright':            '#3d392f',
        'surface-container':         '#231f17',
        'surface-container-low':     '#1f1b13',
        'surface-container-high':    '#2e2920',
        'surface-container-highest': '#39342b',
        'surface-container-lowest':  '#110e06',
        'surface-variant':           '#39342b',
        background:                  '#17130b',

        // MD3 on-surface
        'on-surface':         '#eae1d3',
        'on-surface-variant': '#d1c5af',
        'on-background':      '#eae1d3',

        // MD3 outline
        outline:         '#9a907b',
        'outline-variant': '#4e4635',

        // MD3 misc
        error:           '#ffb4ab',
        'error-container': '#93000a',
        'inverse-surface': '#eae1d3',
        'inverse-on-surface': '#343027',
        'inverse-primary':   '#765a00',
        'surface-tint':      '#efc142',

        // Convenience gold aliases (used in existing code)
        gold: {
          300: '#ffdf95',
          400: '#f2c345',
          500: '#efc142',
          600: '#d4a82a',
        },

        // Semantic signals
        buy:    '#4ade80',
        hold:   '#facc15',
        avoid:  '#f87171',
        online: '#34d399',
      },

      // ── Border radius (exact Stitch definitions) ───────────────────────────
      borderRadius: {
        DEFAULT: '0.25rem',
        lg:      '0.5rem',
        xl:      '0.75rem',
        full:    '9999px',
      },

      // ── Spacing (Stitch component spacing tokens) ──────────────────────────
      spacing: {
        'component_gap': '12px',
        'sidebar_width': '224px',
        'gutter':        '20px',
        'card_padding':  '24px',
        'section_gap':   '32px',
      },

      // ── Shadows ────────────────────────────────────────────────────────────
      boxShadow: {
        card:           'none',
        'card-hover':   '0 12px 48px 0 rgba(0,0,0,0.50)',
        'glow-gold':    '0 0 20px rgba(242,195,69,0.15), 0 0 60px rgba(242,195,69,0.05)',
        tooltip:        '0 8px 32px 0 rgba(0,0,0,0.60)',
      },
    },
  },
  plugins: [],
}
