---
name: WatchScanner — Luxury Horology Terminal

colors:
  # ── Surface hierarchy (Stitch warm sepia palette) ──────────────────────────
  background:                 '#17130b'   # warm black — infinite canvas
  surface:                    '#17130b'   # same as background
  surface-dim:                '#17130b'
  surface-bright:             '#3d392f'   # hovered surfaces
  surface-container-lowest:   '#110e06'   # deepest — scroll areas
  surface-container-low:      '#1f1b13'
  surface-container:          '#231f17'
  surface-container-high:     '#2e2920'   # inputs, raised fills
  surface-container-highest:  '#39342b'   # borders, active rails
  on-surface:                 '#eae1d3'   # primary text (warm white)
  on-surface-variant:         '#d1c5af'   # secondary text, labels
  inverse-surface:            '#eae1d3'
  inverse-on-surface:         '#343027'
  outline:                    '#9a907b'   # captions, placeholders
  outline-variant:            '#4e4635'   # card borders, dividers
  surface-tint:               '#f2c345'   # primary gold tint

  # ── Primary (gold — Stitch brighter) ───────────────────────────────────────
  primary:                    '#f2c345'   # CTA buttons, active nav, prices
  on-primary:                 '#3e2e00'   # text on gold buttons
  primary-container:          '#d4a82a'   # hover state
  on-primary-container:       '#533f00'   # pressed state
  inverse-primary:            '#765a00'
  primary-fixed:              '#ffdf95'   # gradient highlight
  primary-fixed-dim:          '#efc142'

  # ── Secondary (zinc neutral) ────────────────────────────────────────────────
  secondary:                  '#a1a1aa'   # zinc-400
  on-secondary:               '#18181b'   # zinc-900
  secondary-container:        '#27272a'   # zinc-800
  on-secondary-container:     '#f4f4f5'   # zinc-100

  # ── Tertiary (blue — Chrono24 / marketplace accent) ─────────────────────────
  tertiary:                   '#60a5fa'   # blue-400
  on-tertiary:                '#1e3a5f'
  tertiary-container:         '#1d4ed826' # blue-500/15
  on-tertiary-container:      '#93c5fd'   # blue-300

  # ── Semantic: buy / hold / avoid ────────────────────────────────────────────
  error:                      '#f87171'   # red-400 — avoid signal
  on-error:                   '#18181b'
  error-container:            '#7f1d1d26' # red-900/15
  on-error-container:         '#fca5a5'   # red-300

  # ── Named semantic extras (not in MD3 base, kept as custom) ─────────────────
  buy:                        '#4ade80'   # green-400
  buy-container:              '#14532d26' # green-900/15
  on-buy-container:           '#86efac'   # green-300
  hold:                       '#facc15'   # yellow-400
  hold-container:             '#71650026' # yellow-900/15
  on-hold-container:          '#fde047'   # yellow-300
  online:                     '#34d399'   # emerald-400 — live status indicator

typography:
  display-price:
    fontFamily: 'Space Grotesk'
    fontSize: '48px'
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: '-0.025em'

  h1:
    fontFamily: 'Space Grotesk'
    fontSize: '60px'          # hero, 6xl–7xl range
    fontWeight: '700'
    lineHeight: '1.1'

  h2:
    fontFamily: 'Space Grotesk'
    fontSize: '32px'
    fontWeight: '700'
    lineHeight: '1.2'

  h3:
    fontFamily: 'Space Grotesk'
    fontSize: '24px'
    fontWeight: '700'
    lineHeight: '1.3'

  card-title:
    fontFamily: 'Space Grotesk'
    fontSize: '18px'
    fontWeight: '700'
    lineHeight: '1.3'
    letterSpacing: '-0.015em'

  body-lg:
    fontFamily: 'Inter'
    fontSize: '18px'
    fontWeight: '400'
    lineHeight: '1.6'

  body-md:
    fontFamily: 'Inter'
    fontSize: '14px'
    fontWeight: '400'
    lineHeight: '1.5'

  body-sm:
    fontFamily: 'Inter'
    fontSize: '12px'
    fontWeight: '400'
    lineHeight: '1.5'

  label-caps:
    fontFamily: 'Inter'
    fontSize: '12px'
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: '0.05em'
    textTransform: 'uppercase'

  signal-badge:
    fontFamily: 'Inter'
    fontSize: '11px'
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: '0.1em'
    textTransform: 'uppercase'

  micro:
    fontFamily: 'Inter'
    fontSize: '10px'
    fontWeight: '400'
    lineHeight: '1.4'

rounded:
  sm:      '0.375rem'   # 6px — minor badges, small chips
  DEFAULT: '0.5rem'     # 8px — nav items, filter buttons, period selector tabs
  md:      '0.75rem'    # 12px — rounded-xl: inputs, small cards, tooltips
  lg:      '1rem'       # 16px — rounded-2xl: main cards, panels, search form
  full:    '9999px'     # pill — chips, tags, status dots, source badges

spacing:
  base: 4px
  sidebar_width: 224px
  card_padding:  24px
  gutter:        24px
  section_gap:   80px   # py-20 between page sections
  component_gap: 12px   # gap-3 between stat sub-cards
  page_max_sm:   '48rem'  # max-w-3xl — search, alerts
  page_max_lg:   '56rem'  # max-w-4xl — home sections

elevation:
  # This system uses tonal layering and 1px outlines — no traditional box shadows
  card:         'none; border: 1px solid #27272a'           # outline-variant
  card-focus:   'none; border: 1px solid #D4A82A66'         # gold-400/40
  card-hover:   'none; border: 1px solid #3f3f46'           # outline
  sidebar:      '1px 0 0 0 #27272a'                         # inset right border
  cta-button:   '0 4px 16px 0 rgba(212,168,42,0.10)'
  glow-gold:    '0 0 20px rgba(212,168,42,0.15), 0 0 60px rgba(212,168,42,0.05)'
  tooltip:      '0 8px 32px 0 rgba(0,0,0,0.60)'

motion:
  durations:
    instant:  '150ms'
    fast:     '200ms'
    normal:   '300ms'
    moderate: '400ms'
    slow:     '500ms'
    progress: '700ms'

  easings:
    default:   'ease'
    decelerate: 'ease-out'
    standard:  'ease-in-out'
    linear:    'linear'

  animations:
    fade-in:      { keyframes: 'opacity 0→1',                        duration: '300ms', easing: 'ease-out' }
    fade-in-up:   { keyframes: 'opacity 0→1 + translateY(16px→0)',   duration: '400ms', easing: 'ease-out' }
    count-up:     { keyframes: 'opacity 0→1 + translateY(8px→0)',    duration: '500ms', easing: 'ease-out' }
    pulse-dot:    { keyframes: 'opacity 1→0.3→1',                    duration: '2s',    easing: 'ease-in-out', iteration: infinite }
    shimmer:      { keyframes: 'background-position -200%→+200%',    duration: '1.5s',  easing: 'linear',      iteration: infinite }
    border-glow:  { keyframes: 'box-shadow 0→3px gold ring→0',       duration: '2s',    easing: 'ease-in-out', iteration: infinite }
    scan-line:    { keyframes: 'translateY(-100%→100vh)',             duration: '2s',    easing: 'linear',      iteration: infinite }
    card-hover:   { keyframes: 'translateY(0→-2px)',                  duration: '150ms', easing: 'ease' }
    hover-scale:  { keyframes: 'scale(1→1.02)',                       duration: '200ms', easing: 'ease' }
    hero-stagger: { delays: [100ms, 200ms, 350ms, 450ms, 550ms],     description: 'badge → h1 → subtitle → search bar → chips' }

  progress-bar: { fill: primary, track: surface-container-high, height: '4px', radius: full, transition: '700ms ease-out' }
---

## Brand & Style

WatchScanner is a **dark luxury fintech tool** built for serious watch collectors and market speculators who demand the precision of a professional trading floor with the aesthetic of a high-end boutique. The brand personality is authoritative, exclusive, and surgically precise.

The visual language is a fusion of **Minimalist Fintech** and **Luxury Horology** — drawing from the deep black dials of a Submariner and the warm gold of a Daytona register. It avoids unnecessary ornamentation in favor of *functional luxury*: the data — price trends, auction history, investment signals — is the hero. The interface should feel like a high-precision instrument, not a consumer app.

## Colors

The palette is built on three tiers of near-black zinc to create architectural depth without gradients or shadows.

- **`background` (#09090b):** The void — the infinite canvas that makes gold and data pop.
- **`surface` (#18181b):** Every card, the sidebar, all panels. The primary interaction layer.
- **`surface-container-high` (#27272a):** Inputs, hover fills, secondary stat tiles. Signals interactivity.

**`primary` (#D4A82A)** is the only warm element in an otherwise cool, dark palette. It appears exclusively where the user's attention should land: the best price on a listing, the active nav item, the primary CTA button, the chart's median-price line. It is never decorative. Gold equals signal.

**Semantic colors** (buy green, hold yellow, avoid red) are rendered as paired bg/border combos at low opacity — `15%` fill, `30%` border — against the dark surface. This preserves legibility while maintaining the dark luxury mood. The emerald `online` dot in the sidebar communicates system liveness without demanding attention.

Source badges use distinct hues across the full spectrum (blue for Chrono24, pink for Instagram, cyan for TikTok, amber for Vision AI) to make marketplace provenance immediately scannable in dense result lists.

## Typography

**Cabinet Grotesk** handles all display moments: the brand wordmark, page titles, watch reference codes, and prices. Its geometric authority reads as precision on financial data. Prices always use `display-price` with negative letter-spacing.

**Satoshi** (falling back to Inter) handles all body copy, labels, captions, and form elements. At small sizes it is more legible and neutral than Cabinet Grotesk, letting complex data breathe.

Uppercase `label-caps` style is reserved for two contexts only: investment signal badges (BUY / HOLD / AVOID) and section eyebrow labels ("Analisi di Mercato"). The `signal-badge` style adds extreme letter-spacing (`0.1em`) to give these one-word verdicts a commanding, stamp-like authority.

## Layout & Spacing

The layout is **desktop-first**, optimized for the precision of a professional terminal.

- **Sidebar:** Fixed 224px on the left — the permanent spatial anchor. Never collapses.
- **Content columns:** `max-w-3xl` (48rem) for focused task pages (Search, Alerts); `max-w-4xl` (56rem) for informational sections (Home). This intentional narrowing keeps the eye close to gold accents and prevents sprawl.
- **8px base grid:** All internal spacing derives from 4px increments. Primary card padding is 24px (`p-6`). Section breaks are 80px (`py-20`).

## Elevation & Depth

This system uses **tonal layering and 1px outlines** — not traditional shadows. Depth communicates through color luminosity, not a simulated light source.

- Every card has `border: 1px solid surface-container-high` (#27272a). Crisp, architectural.
- On hover, the border promotes to `outline` (#3f3f46) — slightly lighter.
- High-priority elements (best listing, active search form) gain `border-color: primary` (#D4A82A at 40% opacity) as their focused indicator.
- The sidebar is separated by a single 1px inset right border — `box-shadow: 1px 0 0 0 #27272a`.
- The only traditional shadow is a subtle gold ambient glow on primary CTAs (`glow-gold`), used at most once per screen.

## Components

**Primary Button:** Solid `primary` fill (`#D4A82A`) with `on-primary` text (`#09090b`). No gradient. `rounded-lg` (16px). Hover: `primary-container` (#C49A20). Active: `on-primary-container` (#A8830F). Disabled: `opacity-40`. A subtle `cta-button` shadow provides the only non-border depth effect.

**Cards:** `surface` background, 1px `outline-variant` border, `rounded-lg` (16px). Featured cards (search form, fair-price tile) add a `primary` border at 20% opacity and a `radial-gradient` background tint at 8% gold — a focal point that stays within the dark palette.

**Inputs:** `surface-container-high` background, 1px `outline-variant` border, `rounded-md` (12px). Focus: 1px `primary` border with `ring-1 ring-primary/30` halo. Gold is the only focus color in the system.

**Investment Panel:** A signal-colored container (`buy-container`, `hold-container`, or `error-container`) with a matching border. Three visual data indicators live inside: a **ScoreBar** (10 colored blocks, 0–100), a **VolatilityBar** (filled track, color-coded by percentage), and **LiquidityDots** (5 circles, filled count = high/medium/low).

**Source Badges:** `rounded-full` pills using the per-source color triplet (text + `background/10` fill + `border/20`). Size: `body-sm` medium. These are the only multi-color elements in the system.

**Navigation:** Active items use a `2px solid primary` left border with a `primary/10` fill. Inactive items carry a `2px transparent` left border to prevent layout shift on activation. The sub-label under each item uses `micro` (10px) — the smallest type in the system.

**Price Chart:** A Recharts `AreaChart` using `primary` (`#D4A82A`) as the median-price area stroke with a `5%→3%` opacity gradient fill. Min/max lines use `outline` (#3f3f46) with `strokeDasharray`. A dashed `primary` `ReferenceLine` marks the fair price. The chart grid uses horizontal `outline-variant` lines only — vertical gridlines are suppressed to maintain a clean, terminal-style read.

**Skeleton Loading:** `shimmer` animates a `linear-gradient(90deg, surface-container-high 25%, surface-bright 50%, surface-container-high 75%)` across 200% width — scan lines moving across the dark surface, coherent with the product's "scanning" mental model.

**Status Indicator:** A 2×2 `online` (#34d399) dot with `pulse-dot` animation in the sidebar footer. The only persistent animated element in idle state — communicates background agent activity without demanding attention.

## Motion

All motion is purposeful and restrained.

1. **Hero stagger:** Five elements enter with cascading `fade-in-up` delays (100ms → 550ms), guiding the eye from badge to title to search bar without overwhelming.
2. **Card lift:** Cards rise 2px on hover (`translateY(-2px)`) or scale to 1.02. This small displacement confirms interactivity without animation for its own sake.
3. **Progress feedback:** The scan progress bar uses a 700ms `ease-out` fill, communicating that a real, deliberate process is underway.
4. **Skeleton pulse:** Shimmer at 1.5s — fast enough to feel active, slow enough not to distract.
5. **Focus glow:** The search bar pulses a gold ring at 2s intervals while focused, reinforcing that this is the primary interaction point of the product.

Transitions on interactive elements default to 150–200ms `ease`. Fast enough to feel responsive; not so fast they feel mechanical.
