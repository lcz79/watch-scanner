import { useRef, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useLang } from '../lib/lang'
import { motion } from 'framer-motion'
import CountUp from 'react-countup'
import { fmtEur, toEur } from '../lib/currency'

// ── Design tokens ─────────────────────────────────────────────────────────────
const C = {
  navy:    '#07080f',
  navy2:   '#0c0e1a',
  navy3:   '#111425',
  gold:    '#B8975A',
  goldDim: 'rgba(184,151,90,0.14)',
  goldGlow:'rgba(184,151,90,0.22)',
  border:  'rgba(184,151,90,0.12)',
  border2: 'rgba(255,255,255,0.05)',
  green:   '#4EB87A',
  red:     '#E05A5A',
  blue:    '#8899ff',
  t1:      '#e8e2d4',
  t2:      '#8a8070',
  t3:      '#3d3a30',
}
const F = {
  serif:    '"Playfair Display", Georgia, serif',
  cormorant:'"Cormorant Garamond", Georgia, serif',
  mono:     '"IBM Plex Mono", Menlo, monospace',
  sans:     '"Space Grotesk", system-ui, sans-serif',
}

// ── Static fallback data ───────────────────────────────────────────────────────
const AUCTION_CALENDAR = [
  { house: "Christie's",  event: { en: 'Important Watches — Kronos: Titans of Time', it: 'Important Watches — Kronos: Titans of Time' }, date: '29 mag 2026', location: 'Hong Kong', lots: 0, flag: '🇭🇰' },
  { house: 'Bonhams',     event: { en: 'Hong Kong Watches: Rare & Iconic', it: 'Hong Kong Watches: Rare & Iconic' },                   date: '30 mag 2026', location: 'Hong Kong', lots: 0, flag: '🇭🇰' },
  { house: 'Antiquorum',  event: { en: 'Important Modern & Vintage Timepieces', it: 'Orologi Moderni e Vintage Importanti' },          date: '31 mag 2026', location: 'Hong Kong', lots: 0, flag: '🇭🇰' },
  { house: 'Phillips',    event: { en: 'Hong Kong Watch Auction: XXII', it: 'Hong Kong Watch Auction: XXII' },                        date: '1 giu 2026',  location: 'Hong Kong', lots: 0, flag: '🇭🇰' },
]
const AUCTION_RESULTS = [
  { watch: 'Rolex "Paul Newman" Daytona 6241',         house: "Christie's Geneva", date: 'May 2026', hammer: '€ 1.240.000', over: true  },
  { watch: 'Patek Philippe 5711/1A Nautilus (Final Series)', house: "Sotheby's NY",    date: 'Apr 2026', hammer: '€ 340.000',   over: true  },
  { watch: 'AP Royal Oak "Jumbo" 5402ST (1972)',        house: 'Phillips Geneva',   date: 'Apr 2026', hammer: '€ 285.000',   over: false },
  { watch: 'Rolex Submariner 6538 "James Bond"',        house: "Christie's",        date: 'Mar 2026', hammer: '€ 195.000',   over: false },
  { watch: 'Omega Speedmaster CK2998 Pre-Professional', house: 'Antiquorum',        date: 'Mar 2026', hammer: '€ 62.000',    over: false },
]

// ── Helpers ───────────────────────────────────────────────────────────────────
function getRecentSearches(): { ref: string; ts: number }[] {
  try { return JSON.parse(sessionStorage.getItem('recentSearches') || '[]') } catch { return [] }
}

// ── SVG Sparkline ─────────────────────────────────────────────────────────────
function Sparkline({ values, color = C.gold }: { values: number[]; color?: string }) {
  if (!values || values.length < 2) return null
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const W = 280, H = 60
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * W
    const y = H - ((v - min) / range) * (H - 8) - 4
    return `${x},${y}`
  }).join(' ')
  const gradId = `sg-${color.replace(/[^a-z0-9]/gi, '')}`
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: '100%' }} preserveAspectRatio="none">
      <defs>
        <linearGradient id={gradId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%"   stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
        style={{ filter: `drop-shadow(0 0 4px ${color}66)` }} />
      <polygon points={`0,${H} ${pts} ${W},${H}`} fill={`url(#${gradId})`} />
    </svg>
  )
}

// ── 3D Tilt Card ──────────────────────────────────────────────────────────────
function TiltCard({
  children, onClick, accentColor = C.gold,
  style, className,
}: {
  children: React.ReactNode
  onClick?: () => void
  accentColor?: string
  style?: React.CSSProperties
  className?: string
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [tilt, setTilt]     = useState({ x: 0, y: 0 })
  const [glow, setGlow]     = useState({ x: 50, y: 50 })
  const [hovered, setHov]   = useState(false)

  const onMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    const r  = ref.current.getBoundingClientRect()
    const dx = (e.clientX - r.left  - r.width  / 2) / (r.width  / 2)
    const dy = (e.clientY - r.top   - r.height / 2) / (r.height / 2)
    setTilt({ x: dy * -6, y: dx * 8 })
    setGlow({ x: ((e.clientX - r.left) / r.width) * 100, y: ((e.clientY - r.top) / r.height) * 100 })
  }, [])

  const transform = hovered
    ? `perspective(700px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale3d(1.025,1.025,1.025)`
    : 'perspective(700px) rotateX(0) rotateY(0) scale3d(1,1,1)'
  const shadow = hovered
    ? `${-tilt.y * 2}px ${tilt.x * 2}px 32px rgba(184,151,90,0.18), 0 0 60px rgba(184,151,90,0.06)`
    : '0 2px 16px rgba(0,0,0,0.35)'

  return (
    <div
      ref={ref}
      onMouseMove={onMove}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => { setHov(false); setTilt({ x: 0, y: 0 }) }}
      onClick={onClick}
      className={className}
      style={{
        position: 'relative', overflow: 'hidden', cursor: 'pointer',
        background: C.navy2,
        border: `1px solid ${hovered ? accentColor + '44' : C.border}`,
        transformStyle: 'preserve-3d',
        transform, transition: hovered ? 'transform 0.08s ease, box-shadow 0.08s ease, border-color 0.2s' : 'transform 0.5s cubic-bezier(0.16,1,0.3,1), box-shadow 0.5s, border-color 0.2s',
        boxShadow: shadow,
        display: 'flex', flexDirection: 'column',
        ...style,
      }}
    >
      {/* Radial glow following cursor */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 1,
        background: hovered ? `radial-gradient(circle at ${glow.x}% ${glow.y}%, ${accentColor}22 0%, transparent 55%)` : 'none',
        transition: 'opacity 0.2s',
      }} />
      {/* Top edge shimmer on hover */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 1, zIndex: 2,
        background: `linear-gradient(90deg, transparent, ${accentColor}${hovered ? 'aa' : '00'}, transparent)`,
        transition: 'background 0.3s',
      }} />
      {children}
    </div>
  )
}

// ── Section header ────────────────────────────────────────────────────────────
function SectionHeader({ title, meta, cta, onCta }: { title: string; meta?: string; cta?: string; onCta?: () => void }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
      <span style={{ fontFamily: F.serif, fontSize: 16, fontWeight: 700, color: C.gold, whiteSpace: 'nowrap' }}>
        {title}
      </span>
      <div style={{ flex: 1, height: 1, background: C.border }} />
      {meta && <span style={{ fontFamily: F.mono, fontSize: 8, color: C.t3, letterSpacing: '0.1em', whiteSpace: 'nowrap' }}>{meta}</span>}
      {cta && (
        <button onClick={onCta} style={{ fontFamily: F.mono, fontSize: 8, color: C.gold, letterSpacing: '0.12em', textTransform: 'uppercase', background: 'none', border: 'none', cursor: 'pointer' }}>
          {cta} →
        </button>
      )}
    </div>
  )
}

// ── Supply bar ────────────────────────────────────────────────────────────────
function SupplyBar({ pct, color }: { pct: number; color: string }) {
  const [width, setW] = useState(0)
  useEffect(() => { const id = setTimeout(() => setW(pct), 300); return () => clearTimeout(id) }, [pct])
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: F.mono, fontSize: 8, color: C.t3, letterSpacing: '0.08em', marginBottom: 5 }}>
        <span>Supply index</span><span>{pct} / 100</span>
      </div>
      <div style={{ height: 3, background: 'rgba(255,255,255,0.04)', position: 'relative' }}>
        <div style={{
          height: '100%', width: `${width}%`,
          background: `linear-gradient(90deg, ${color}, ${color}cc)`,
          transition: 'width 1.2s cubic-bezier(0.16,1,0.3,1)',
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute', right: 0, top: '50%', transform: 'translate(50%, -50%)',
            width: 8, height: 8, borderRadius: '50%', background: color,
            boxShadow: `0 0 8px ${color}`,
          }} />
        </div>
      </div>
    </div>
  )
}

// ── Watch image overlay ───────────────────────────────────────────────────────
function WatchImageOverlay({ url }: { url?: string }) {
  if (!url) return null
  return (
    <div style={{
      position: 'absolute', right: -16, bottom: -8,
      width: 160, height: 160,
      pointerEvents: 'none', zIndex: 0,
      maskImage: 'radial-gradient(ellipse 80% 80% at 60% 60%, black 20%, transparent 75%)',
      WebkitMaskImage: 'radial-gradient(ellipse 80% 80% at 60% 60%, black 20%, transparent 75%)',
    }}>
      <img
        src={url}
        alt=""
        onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
        style={{
          width: '100%', height: '100%', objectFit: 'contain',
          opacity: 0.13,
          filter: 'grayscale(20%) saturate(0.9)',
          mixBlendMode: 'luminosity',
        }}
      />
    </div>
  )
}

// ── Ornament numeral ──────────────────────────────────────────────────────────
function Ornament({ n }: { n: string }) {
  return (
    <div style={{
      position: 'absolute', top: 8, right: 12,
      fontFamily: F.serif, fontSize: 56, fontWeight: 900, lineHeight: 1,
      color: 'rgba(184,151,90,0.07)', pointerEvents: 'none', zIndex: 0,
      userSelect: 'none',
    }}>{n}</div>
  )
}

// ── Types ─────────────────────────────────────────────────────────────────────
interface IntelCard {
  reference: string; brand: string; model: string; has_data?: boolean; image_url?: string
}
interface AppreciationCard extends IntelCard {
  current_price_chf: number; price_6m_ago_chf: number; change_pct: number
  period_days: number; listings_count: number; sparkline: number[]
}
interface OfferedCard extends IntelCard {
  listings_count: number; current_price_chf: number; change_pct_6m?: number
  supply_note: string; supply_note_en?: string
}
interface RarestCard extends IntelCard {
  listings_count: number; current_price_chf: number; change_pct_6m?: number
  scarcity_note: string; scarcity_note_en?: string
}
interface MarketIntelligence {
  most_appreciated: AppreciationCard; most_offered: OfferedCard; rarest: RarestCard; computed_at: string
}

function useMarketIntelligence() {
  return useQuery<MarketIntelligence>({
    queryKey: ['market-intelligence'],
    queryFn: () => fetch('/api/market/intelligence').then(r => { if (!r.ok) throw new Error('err'); return r.json() }),
    retry: false, staleTime: 15 * 60 * 1000,
  })
}

// ── HomePage ──────────────────────────────────────────────────────────────────
export default function HomePage() {
  const navigate = useNavigate()
  const { t, lang } = useLang()
  const recentSearches = getRecentSearches()

  const { data: intel, isLoading: intelLoading } = useMarketIntelligence()

  const { data: newsData } = useQuery({
    queryKey: ['news'],
    queryFn: () => fetch('/api/news?limit=6').then(r => r.ok ? r.json() : Promise.reject()),
    retry: false, staleTime: 10 * 60 * 1000,
  })

  const { data: upcomingData } = useQuery({
    queryKey: ['auctions-upcoming'],
    queryFn: () => fetch('/api/auctions/upcoming').then(r => r.ok ? r.json() : Promise.reject()),
    retry: false, staleTime: 30 * 60 * 1000,
  })

  const auctionCalendar: typeof AUCTION_CALENDAR =
    upcomingData?.auctions?.length
      ? upcomingData.auctions.map((a: Record<string, unknown>) => ({
          house: a.house as string,
          event: (a.event as Record<string,string>) ?? { en: a.sale_name as string, it: a.sale_name as string },
          date: (() => {
            const raw = a.date as string | undefined
            if (!raw) return '—'
            try {
              const [y, m, d] = raw.slice(0, 10).split('-').map(Number)
              return new Date(y, m - 1, d).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
            } catch { return raw }
          })(),
          location: (a.location as string) ?? '—',
          lots: (a.lots as number) ?? 0,
          flag: (a.flag as string) ?? (['hong kong','hk'].some(k => ((a.location as string)?.toLowerCase() ?? '').includes(k)) ? '🇭🇰'
            : ((a.location as string)?.toLowerCase() ?? '').includes('genev') ? '🇨🇭'
            : ((a.location as string)?.toLowerCase() ?? '').includes('new york') ? '🇺🇸'
            : ((a.location as string)?.toLowerCase() ?? '').includes('london') ? '🇬🇧' : '🌍'),
        }))
      : AUCTION_CALENDAR

  const newsItems: Array<{ title: string; summary?: string; url: string; image_url?: string; source?: string; published_at?: string }> = newsData?.news ?? []

  /* ---------- shared card style helpers ---------- */
  const cardTag = (label: string, color: string) => (
    <span style={{ fontFamily: F.mono, fontSize: 8, letterSpacing: '0.18em', color, textTransform: 'uppercase', fontWeight: 700 }}>
      {label}
    </span>
  )
  const badge = (content: React.ReactNode, color: string) => (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4, padding: '3px 10px',
      background: `${color}18`, color, fontFamily: F.mono, fontSize: 11, fontWeight: 700,
    }}>
      {content}
    </span>
  )
  const cardRef = (ref: string) => (
    <div style={{ fontFamily: F.serif, fontSize: 22, fontWeight: 700, color: '#fff', marginBottom: 2, position: 'relative', zIndex: 2 }}>
      {ref}
    </div>
  )
  const cardBrand = (brand: string) => (
    <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 14, position: 'relative', zIndex: 2 }}>
      {brand}
    </div>
  )
  const cardPrice = (chf: number, color: string) => (
    <div style={{ fontFamily: F.cormorant, fontSize: 36, fontWeight: 600, color, lineHeight: 1, position: 'relative', zIndex: 2 }}>
      € <CountUp end={toEur(chf)} separator="." duration={1.2} />
    </div>
  )
  const divider = () => <div style={{ height: 1, background: C.border, margin: '12px 0' }} />

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div style={{ padding: '20px 24px', maxWidth: 1600, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* ── 1. MARKET INTELLIGENCE ─────────────────────────────────────── */}
      <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <SectionHeader
          title={lang === 'it' ? 'Segnali di Mercato' : 'Market Signals'}
          meta={intel?.computed_at ? `AGG · ${new Date(intel.computed_at).toLocaleTimeString(lang === 'it' ? 'it-IT' : 'en-GB', { hour: '2-digit', minute: '2-digit' })}` : undefined}
        />

        {intelLoading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
            {[0,1,2].map(i => (
              <div key={i} style={{ background: C.navy2, border: `1px solid ${C.border}`, height: 200, padding: 20 }}>
                <div className="animate-pulse">
                  <div style={{ height: 8, background: C.navy3, width: '40%', marginBottom: 16 }} />
                  <div style={{ height: 20, background: C.navy3, width: '65%', marginBottom: 8 }} />
                  <div style={{ height: 36, background: C.navy3, width: '50%', marginBottom: 8 }} />
                </div>
              </div>
            ))}
          </div>
        ) : intel ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>

            {/* ── Card 1: Apprezzamento ─────────────────────────────── */}
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
              <TiltCard accentColor={C.green} onClick={() => navigate(`/search?ref=${encodeURIComponent(intel.most_appreciated.reference)}`)}>
                <Ornament n="I" />
                <WatchImageOverlay url={intel.most_appreciated.image_url} />
                <div style={{ padding: '16px 18px 0', position: 'relative', zIndex: 2 }}>
                  {cardTag('▲ ' + (lang === 'it' ? 'Maggior Apprezzamento' : 'Best Appreciation'), C.green)}
                </div>
                <div style={{ padding: '10px 18px', position: 'relative', zIndex: 2, flex: 1 }}>
                  {cardRef(intel.most_appreciated.reference)}
                  {cardBrand(`${intel.most_appreciated.brand} · ${intel.most_appreciated.model}`)}
                  {cardPrice(intel.most_appreciated.current_price_chf, C.green)}
                  <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginTop: 3 }}>
                    {lang === 'it' ? 'da' : 'from'} {fmtEur(intel.most_appreciated.price_6m_ago_chf)} · {lang === 'it' ? 'gen' : 'jan'} {new Date().getFullYear()}
                  </div>
                  {divider()}
                  {badge(`▲ +${intel.most_appreciated.change_pct.toFixed(1)}%`, C.green)}
                  <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginTop: 6 }}>
                    {intel.most_appreciated.listings_count} {lang === 'it' ? 'annunci attivi' : 'active listings'}
                  </div>
                </div>
                {intel.most_appreciated.sparkline.length > 2 && (
                  <div style={{ height: 48, borderTop: `1px solid ${C.border2}`, flexShrink: 0 }}>
                    <Sparkline values={intel.most_appreciated.sparkline} color={C.green} />
                  </div>
                )}
              </TiltCard>
            </motion.div>

            {/* ── Card 2: Più Offerto ───────────────────────────────── */}
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
              <TiltCard accentColor={C.gold} onClick={() => navigate(`/search?ref=${encodeURIComponent(intel.most_offered.reference)}`)}>
                <Ornament n="II" />
                <WatchImageOverlay url={intel.most_offered.image_url} />
                <div style={{ padding: '16px 18px 0', position: 'relative', zIndex: 2 }}>
                  {cardTag('◈ ' + (lang === 'it' ? 'Offerta Più Alta' : 'Highest Supply'), C.gold)}
                </div>
                <div style={{ padding: '10px 18px', position: 'relative', zIndex: 2, flex: 1 }}>
                  {cardRef(intel.most_offered.reference)}
                  {cardBrand(`${intel.most_offered.brand} · ${intel.most_offered.model}`)}
                  {cardPrice(intel.most_offered.current_price_chf, C.gold)}
                  <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginTop: 3 }}>
                    {intel.most_offered.listings_count} {lang === 'it' ? 'annunci attivi ora' : 'active listings now'}
                  </div>
                  {divider()}
                  {badge(`◈ ${intel.most_offered.listings_count} ${lang === 'it' ? 'ANNUNCI' : 'LISTINGS'}`, C.gold)}
                  <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginTop: 8, lineHeight: 1.5 }}>
                    {lang === 'it' ? intel.most_offered.supply_note : (intel.most_offered.supply_note_en ?? intel.most_offered.supply_note)}
                  </div>
                </div>
                <div style={{ padding: '10px 18px 14px', borderTop: `1px solid ${C.border2}` }}>
                  <SupplyBar
                    pct={Math.min(100, Math.round((intel.most_offered.listings_count / 150) * 100))}
                    color={C.gold}
                  />
                </div>
              </TiltCard>
            </motion.div>

            {/* ── Card 3: Più Raro ──────────────────────────────────── */}
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.19 }}>
              <TiltCard accentColor={C.blue} onClick={() => navigate(`/search?ref=${encodeURIComponent(intel.rarest.reference)}`)}>
                <Ornament n="III" />
                <WatchImageOverlay url={intel.rarest.image_url} />
                <div style={{ padding: '16px 18px 0', position: 'relative', zIndex: 2 }}>
                  {cardTag('◆ ' + (lang === 'it' ? 'Più Raro' : 'Rarest'), C.blue)}
                </div>
                <div style={{ padding: '10px 18px', position: 'relative', zIndex: 2, flex: 1 }}>
                  {cardRef(intel.rarest.reference)}
                  {cardBrand(`${intel.rarest.brand} · ${intel.rarest.model}`)}
                  {cardPrice(intel.rarest.current_price_chf, C.blue)}
                  <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginTop: 3 }}>
                    {lang === 'it' ? 'solo' : 'only'} {intel.rarest.listings_count} {lang === 'it' ? 'annunci nel mercato' : 'listings on market'}
                  </div>
                  {divider()}
                  {badge(`◆ ${intel.rarest.listings_count} ${lang === 'it' ? 'ANNUNCI' : 'LISTINGS'}`, C.blue)}
                  <div style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginTop: 8, lineHeight: 1.5 }}>
                    {lang === 'it' ? intel.rarest.scarcity_note : (intel.rarest.scarcity_note_en ?? intel.rarest.scarcity_note)}
                  </div>
                </div>
                <div style={{ padding: '10px 18px 14px', borderTop: `1px solid ${C.border2}` }}>
                  <SupplyBar
                    pct={Math.max(5, Math.min(100, Math.round(100 - (intel.rarest.listings_count / 150) * 100)))}
                    color={C.blue}
                  />
                </div>
              </TiltCard>
            </motion.div>

          </div>
        ) : (
          <div style={{ background: C.navy2, border: `1px solid ${C.border}`, padding: 24, textAlign: 'center' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 28, color: C.t3, display: 'block', marginBottom: 8 }}>bar_chart</span>
            <p style={{ fontFamily: F.mono, fontSize: 10, color: C.t2 }}>{lang === 'it' ? 'Dati in aggiornamento…' : 'Market data updating…'}</p>
          </div>
        )}
      </motion.section>

      {/* ── 2. AUCTION CALENDAR ────────────────────────────────────────── */}
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.15 }}>
        <SectionHeader
          title={t.auctionCalendarTitle}
          cta={lang === 'it' ? 'Tutte le aste' : 'All auctions'}
          onCta={() => navigate('/auctions')}
        />
        <div style={{ background: C.navy2, border: `1px solid ${C.border}` }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                {[t.auction_house, 'Event', t.auction_date, t.auction_location, t.auction_lots].map((h, i) => (
                  <th key={i} style={{ padding: '8px 16px', textAlign: i === 4 ? 'right' : 'left', fontFamily: F.mono, fontSize: 8, color: C.t3, letterSpacing: '0.16em', textTransform: 'uppercase', fontWeight: 400 }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {auctionCalendar.map((a, i) => (
                <tr
                  key={i}
                  style={{ borderBottom: i < auctionCalendar.length - 1 ? `1px solid ${C.border2}` : 'none', cursor: 'pointer', transition: 'background 0.12s' }}
                  onMouseEnter={e => (e.currentTarget.style.background = C.goldDim)}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ padding: '12px 16px', fontFamily: F.serif, fontSize: 13, fontWeight: 700, color: '#fff' }}>{a.house}</td>
                  <td style={{ padding: '12px 16px', fontFamily: F.sans, fontSize: 11, color: C.t2 }}>{a.event[lang]}</td>
                  <td style={{ padding: '12px 16px', fontFamily: F.mono, fontSize: 10, color: C.gold }}>{a.date}</td>
                  <td style={{ padding: '12px 16px', fontFamily: F.mono, fontSize: 10, color: C.t2 }}>{a.flag} {a.location}</td>
                  <td style={{ padding: '12px 16px', textAlign: 'right', fontFamily: F.mono, fontSize: 10, color: C.t3 }}>{a.lots > 0 ? `${a.lots} lots` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.section>

      {/* ── 3. AUCTION RESULTS ─────────────────────────────────────────── */}
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.2 }}>
        <SectionHeader title={t.auctionResultsTitle} meta={lang === 'it' ? 'RISULTATI RECENTI' : 'RECENT RESULTS'} />
        <div style={{ background: C.navy2, border: `1px solid ${C.border}` }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                {['Watch', t.auction_house, t.auction_date, t.auction_hammer, t.auction_result].map((h, i) => (
                  <th key={i} style={{ padding: '8px 16px', textAlign: i >= 3 ? 'right' : 'left', fontFamily: F.mono, fontSize: 8, color: C.t3, letterSpacing: '0.16em', textTransform: 'uppercase', fontWeight: 400 }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {AUCTION_RESULTS.map((r, i) => (
                <tr
                  key={i}
                  style={{ borderBottom: i < AUCTION_RESULTS.length - 1 ? `1px solid ${C.border2}` : 'none', transition: 'background 0.12s', cursor: 'default' }}
                  onMouseEnter={e => (e.currentTarget.style.background = C.goldDim)}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ padding: '11px 16px', fontFamily: F.sans, fontSize: 12, fontWeight: 500, color: C.t1 }}>
                    {i === 0 && <span className="material-symbols-outlined" style={{ fontSize: 12, color: C.gold, marginRight: 6, verticalAlign: 'middle', fontVariationSettings: "'FILL' 1" }}>star</span>}
                    {r.watch}
                  </td>
                  <td style={{ padding: '11px 16px', fontFamily: F.mono, fontSize: 10, color: C.t2 }}>{r.house}</td>
                  <td style={{ padding: '11px 16px', fontFamily: F.mono, fontSize: 10, color: C.t3 }}>{r.date}</td>
                  <td style={{ padding: '11px 16px', textAlign: 'right', fontFamily: F.mono, fontSize: 12, fontWeight: 600, color: C.gold }}>{r.hammer}</td>
                  <td style={{ padding: '11px 16px', textAlign: 'right' }}>
                    {r.over ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, fontFamily: F.mono, fontSize: 9, fontWeight: 700, color: C.green, letterSpacing: '0.1em' }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 11 }}>arrow_upward</span>
                        {lang === 'it' ? 'SUPERATO' : 'ABOVE EST.'}
                      </span>
                    ) : (
                      <span style={{ fontFamily: F.mono, fontSize: 9, color: C.t3 }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.section>

      {/* ── 4. RECENT SEARCHES ─────────────────────────────────────────── */}
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.25 }}>
        <SectionHeader
          title={t.recentSearchesTitle}
          cta={lang === 'it' ? 'Cerca' : 'Search'}
          onCta={() => navigate('/search')}
        />
        {recentSearches.length === 0 ? (
          <div style={{ background: C.navy2, border: `1px dashed ${C.border}`, padding: 40, textAlign: 'center' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 32, color: C.t3, display: 'block', marginBottom: 8 }}>manage_search</span>
            <p style={{ fontFamily: F.sans, fontSize: 13, color: C.t2, marginBottom: 4 }}>{t.noRecentSearches}</p>
            <p style={{ fontFamily: F.mono, fontSize: 10, color: C.t3 }}>{t.noRecentSub}</p>
            <button
              onClick={() => navigate('/search')}
              style={{ marginTop: 16, background: C.gold, color: '#000', fontFamily: F.mono, fontSize: 9, fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase', padding: '8px 20px', border: 'none', cursor: 'pointer' }}
            >
              {t.searchNow}
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 10 }}>
            {recentSearches.slice(0, 8).map(s => (
              <div
                key={s.ref}
                onClick={() => navigate(`/search?ref=${encodeURIComponent(s.ref)}`)}
                style={{ background: C.navy2, border: `1px solid ${C.border}`, padding: '14px 16px', cursor: 'pointer', transition: 'all 0.12s' }}
                onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.background = C.goldDim; (e.currentTarget as HTMLDivElement).style.borderColor = C.gold + '44' }}
                onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.background = C.navy2; (e.currentTarget as HTMLDivElement).style.borderColor = C.border }}
              >
                <div style={{ fontFamily: F.serif, fontSize: 15, fontWeight: 700, color: '#fff', marginBottom: 6 }}>{s.ref}</div>
                <div style={{ fontFamily: F.mono, fontSize: 8, color: C.t3, letterSpacing: '0.08em' }}>
                  {new Date(s.ts).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
          </div>
        )}
      </motion.section>

      {/* ── 5. MARKET NEWS ─────────────────────────────────────────────── */}
      {newsData !== undefined && (
        <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.3 }}>
          <SectionHeader title={lang === 'it' ? 'Notizie dal Mercato' : 'Market News'} />
          {newsItems.length === 0 ? (
            <div style={{ background: C.navy2, border: `1px dashed ${C.border}`, padding: 40, textAlign: 'center' }}>
              <span className="material-symbols-outlined" style={{ fontSize: 28, color: C.t3, display: 'block', marginBottom: 8 }}>newspaper</span>
              <p style={{ fontFamily: F.mono, fontSize: 10, color: C.t2 }}>{lang === 'it' ? 'Feed RSS in aggiornamento ogni 12h' : 'RSS feed updates every 12h'}</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
              {newsItems.map((item, i) => {
                const pub = item.published_at ? new Date(item.published_at).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : null
                return (
                  <a key={i} href={item.url} target="_blank" rel="noopener noreferrer"
                    style={{ background: C.navy2, border: `1px solid ${C.border}`, display: 'flex', flexDirection: 'column', textDecoration: 'none', transition: 'border-color 0.15s' }}
                    onMouseEnter={e => (e.currentTarget.style.borderColor = C.gold + '44')}
                    onMouseLeave={e => (e.currentTarget.style.borderColor = C.border)}
                  >
                    <div style={{ height: 140, background: C.navy3, overflow: 'hidden', flexShrink: 0 }}>
                      {item.image_url ? (
                        <img src={item.image_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.3s' }}
                          onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none' }} />
                      ) : (
                        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <span className="material-symbols-outlined" style={{ fontSize: 40, color: C.t3 }}>newspaper</span>
                        </div>
                      )}
                    </div>
                    <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                        {item.source && <span style={{ fontFamily: F.mono, fontSize: 8, fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase', background: C.goldDim, color: C.gold, padding: '2px 8px' }}>{item.source}</span>}
                        {pub && <span style={{ fontFamily: F.mono, fontSize: 9, color: C.t3, marginLeft: 'auto' }}>{pub}</span>}
                      </div>
                      <h3 style={{ fontFamily: F.sans, fontSize: 12, fontWeight: 600, color: C.t1, lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {item.title}
                      </h3>
                      {item.summary && (
                        <p style={{ fontFamily: F.sans, fontSize: 11, color: C.t2, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', flex: 1 }}>
                          {item.summary}
                        </p>
                      )}
                      <div style={{ fontFamily: F.mono, fontSize: 8, color: C.t3, letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: 'auto', paddingTop: 8 }}>
                        {lang === 'it' ? 'Leggi' : 'Read'} →
                      </div>
                    </div>
                  </a>
                )
              })}
            </div>
          )}
        </motion.section>
      )}

    </div>
  )
}
