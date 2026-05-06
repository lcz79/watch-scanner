// Watch movement background — close-up gear train aesthetic

const SILVER = 'rgba(212,212,216,'
const GOLD   = 'rgba(242,195,69,'
const RED    = 'rgba(190,18,60,'

function gearPath(innerR: number, outerR: number, teeth: number): string {
  const segs: string[] = []
  const ta = (Math.PI * 2) / teeth
  const ht = ta * 0.20
  for (let i = 0; i < teeth; i++) {
    const a = (i / teeth) * Math.PI * 2
    const ir = (θ: number) => `${(innerR * Math.cos(θ)).toFixed(2)},${(innerR * Math.sin(θ)).toFixed(2)}`
    const or = (θ: number) => `${(outerR * Math.cos(θ)).toFixed(2)},${(outerR * Math.sin(θ)).toFixed(2)}`
    segs.push(`${i === 0 ? 'M' : 'L'}${ir(a - ta * 0.5)} L${or(a - ht)} L${or(a + ht)} L${ir(a + ta * 0.5)}`)
  }
  return segs.join(' ') + ' Z'
}

// Curved spokes inside a gear (like the image — 3 or 4 spoke designs)
function spokesPath(n: number, hubR: number, rimR: number): string {
  const segs: string[] = []
  const w = 0.14 // spoke angular half-width factor
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2
    const b = a + Math.PI * 2 / n
    // spoke from hub to rim with slight taper
    const x1 = (hubR * 1.1 * Math.cos(a - w)).toFixed(2)
    const y1 = (hubR * 1.1 * Math.sin(a - w)).toFixed(2)
    const x2 = (hubR * 1.1 * Math.cos(a + w)).toFixed(2)
    const y2 = (hubR * 1.1 * Math.sin(a + w)).toFixed(2)
    const x3 = (rimR * Math.cos(a + w * 0.5)).toFixed(2)
    const y3 = (rimR * Math.sin(a + w * 0.5)).toFixed(2)
    const x4 = (rimR * Math.cos(a - w * 0.5)).toFixed(2)
    const y4 = (rimR * Math.sin(a - w * 0.5)).toFixed(2)
    // arc connectors between spokes at rim
    const mx = (rimR * 0.85 * Math.cos((a + b) / 2)).toFixed(2)
    const my = (rimR * 0.85 * Math.sin((a + b) / 2)).toFixed(2)
    segs.push(`M${x1},${y1} L${x4},${y4} Q${mx},${my} ${x3},${y3} L${x2},${y2} Z`)
  }
  return segs.join(' ')
}

// [cx, cy, innerR, outerR, teeth, dur_s, cw, isGold, spokesN]
type GearDef = [number, number, number, number, number, number, boolean, boolean, number]

const GEARS: GearDef[] = [
  // Large silver gears — partially cut off at edges
  [1130, 240,  248, 272, 54, 70,  true,  false, 4], // top-right large
  [380,  400,  210, 232, 46, 90,  false, false, 3], // left large
  // Medium gears — gold movement wheels
  [780,  360,   98, 111, 22, 43,  true,  true,  0], // center mesh
  [1030, 560,  115, 128, 26, 48,  false, false, 0], // right medium
  // Small gold pinions
  [650,  530,   40,  50,  9, 21,  false, true,  0], // center-left pinion
  [870,  510,   38,  47,  9, 21,  true,  true,  0], // center-right pinion
  // Fine ratchet / crown wheel style
  [580,  720,   82,  96, 28, 38,  true,  false, 0], // bottom-left ratchet
  [980,  730,   65,  76, 18, 28,  false, false, 0], // bottom-right
  // Partially visible at edges
  [180,  200,  130, 145, 30, 55,  true,  false, 3], // top-left cut off
  [1320, 680,   88, 100, 22, 33,  true,  true,  0], // bottom-right cut off
  [1280, 180,   60,  70, 16, 24,  false, false, 0], // top-right small
  [200,  750,   48,  58, 12, 18,  false, true,  0], // bottom-left small
]

// Precompute paths at module level
const GEAR_PATHS = GEARS.map(([,, iR, oR, teeth]) => gearPath(iR, oR, teeth))
const SPOKE_PATHS = GEARS.map(([,, iR,, , , , , n]) => n > 0 ? spokesPath(n, iR * 0.28, iR * 0.78) : '')

const CSS = `
  @keyframes cw  { to { transform: rotate( 360deg); } }
  @keyframes ccw { to { transform: rotate(-360deg); } }
  ${GEARS.map(([,,,,,dur,cw,,], i) =>
    `.wg${i}{transform-box:fill-box;transform-origin:center;animation:${cw?'cw':'ccw'} ${dur}s linear infinite}`
  ).join(' ')}
`

// Jewels (ruby bearings) at movement key points
const JEWELS: [number, number, number][] = [
  [780, 360,  9], // center wheel
  [650, 530,  7], // pinion
  [870, 510,  7],
  [380, 400, 11], // left gear
  [1130, 240, 12], // top-right gear
  [1030, 560,  8],
  [490, 300,  6],
  [920, 280,  6],
]

// Decorative screws (circle + slot) — characteristic of movements
const SCREWS: [number, number, number][] = [
  [280,  175, 8],
  [680,  200, 7],
  [1200, 300, 8],
  [500,  630, 7],
  [1100, 670, 7],
  [300,  560, 6],
  [1050, 180, 6],
  [750,  660, 6],
]

// Bridge plate outlines (gold trapezoidal/irregular shapes)
const BRIDGES = [
  'M 560,280 L 900,250 L 920,440 L 720,460 L 540,420 Z',
  'M 300,350 L 500,320 L 520,540 L 330,560 Z',
  'M 950,460 L 1180,430 L 1200,620 L 980,650 Z',
]

export default function WatchBackground() {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none select-none" aria-hidden="true">
      <svg
        viewBox="0 0 1440 900"
        className="absolute inset-0 w-full h-full"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <style>{CSS}</style>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Bridge plates — gold/brass engraved look */}
        {BRIDGES.map((d, i) => (
          <path key={i} d={d}
            fill={GOLD + '0.025)'}
            stroke={GOLD + '0.10)'}
            strokeWidth="1"
          />
        ))}

        {/* Gears */}
        {GEARS.map(([cx, cy, iR, oR,,,, isGold, spokesN], i) => {
          const col = isGold ? GOLD : SILVER
          return (
            <g key={i} transform={`translate(${cx},${cy})`}>
              {/* Gear body fill */}
              <circle r={oR} fill={col + '0.06)'} />
              {/* Spokes (for gears that have them) */}
              {spokesN > 0 && (
                <path
                  className={`wg${i}`}
                  d={SPOKE_PATHS[i]}
                  fill={col + '0.12)'}
                  stroke={col + '0.20)'}
                  strokeWidth="0.8"
                />
              )}
              {/* Inner rim circle */}
              <circle r={iR} fill="none" stroke={col + '0.14)'} strokeWidth="1.5" />
              {/* Hub inner circle */}
              <circle r={iR * 0.30} fill={col + '0.08)'} stroke={col + '0.18)'} strokeWidth="1" />
              <circle r={iR * 0.12} fill={col + '0.20)'} />
              {/* Rotating teeth */}
              <path
                className={`wg${i}`}
                d={GEAR_PATHS[i]}
                fill={col + '0.07)'}
                stroke={col + (isGold ? '0.22)' : '0.17)')}
                strokeWidth={isGold ? '1.2' : '1'}
              />
            </g>
          )
        })}

        {/* Jewel bearings */}
        {JEWELS.map(([cx, cy, r], i) => (
          <g key={i} filter="url(#glow)">
            {/* Gold setting ring */}
            <circle cx={cx} cy={cy} r={r + 4} fill={GOLD + '0.08)'} stroke={GOLD + '0.28)'} strokeWidth="1" />
            <circle cx={cx} cy={cy} r={r + 1} fill={GOLD + '0.12)'} stroke={GOLD + '0.20)'} strokeWidth="0.5" />
            {/* Ruby body */}
            <circle cx={cx} cy={cy} r={r} fill={RED + '0.50)'} stroke={RED + '0.40)'} strokeWidth="0.5" />
            {/* Highlight */}
            <circle cx={cx - r * 0.3} cy={cy - r * 0.3} r={r * 0.35} fill="rgba(255,180,180,0.25)" />
          </g>
        ))}

        {/* Decorative screws */}
        {SCREWS.map(([cx, cy, r], i) => (
          <g key={i} opacity="0.50">
            <circle cx={cx} cy={cy} r={r} fill={SILVER + '0.12)'} stroke={SILVER + '0.30)'} strokeWidth="1" />
            <circle cx={cx} cy={cy} r={r * 0.55} fill="none" stroke={SILVER + '0.20)'} strokeWidth="0.5" />
            {/* Screw slot */}
            <line
              x1={cx - r * 0.7} y1={cy}
              x2={cx + r * 0.7} y2={cy}
              stroke={SILVER + '0.40)'} strokeWidth="1.2" strokeLinecap="round"
            />
          </g>
        ))}
      </svg>

      {/* Dark overlay — denser at edges, lets movement glow through center */}
      <div
        className="absolute inset-0"
        style={{
          background: [
            'radial-gradient(ellipse 75% 65% at 55% 48%, rgba(9,9,11,0.60) 0%, rgba(9,9,11,0.88) 100%)',
          ].join(', ')
        }}
      />
    </div>
  )
}
