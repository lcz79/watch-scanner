import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useLang } from '../lib/lang'

// ── Mock data ────────────────────────────────────────────────────────────────

// Market models to query from the real API
const MARKET_MODELS = [
  {
    ref: '116610LN',
    icon: 'trending_up',
    label: { en: 'Rolex Submariner', it: 'Rolex Submariner' },
    fallbackTag: { en: 'Trending', it: 'In Rialzo' },
    fallbackTagColor: 'bg-green-400/10 text-green-400 border-green-400/20',
  },
  {
    ref: '15500ST',
    icon: 'query_stats',
    label: { en: 'AP Royal Oak 15500ST', it: 'AP Royal Oak 15500ST' },
    fallbackTag: { en: 'Accumulate', it: 'Accumulo' },
    fallbackTagColor: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20',
  },
  {
    ref: '5711/1A',
    icon: 'new_releases',
    label: { en: 'Patek Nautilus 5711/1A', it: 'Patek Nautilus 5711/1A' },
    fallbackTag: { en: 'High Demand', it: 'Alta Domanda' },
    fallbackTagColor: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
  },
]

const AUCTION_CALENDAR = [
  {
    house: "Christie's",
    event: { en: 'Watches Online: The Geneva Edit', it: 'Watches Online: The Geneva Edit' },
    date: '14 Jun 2026',
    location: 'Geneva',
    lots: 120,
    flag: '🇨🇭',
  },
  {
    house: "Sotheby's",
    event: { en: 'Important Watches', it: 'Orologi Importanti' },
    date: '28 Jun 2026',
    location: 'New York',
    lots: 85,
    flag: '🇺🇸',
  },
  {
    house: 'Phillips',
    event: { en: 'The Geneva Watch Auction: XVIII', it: 'The Geneva Watch Auction: XVIII' },
    date: '12 Jul 2026',
    location: 'Geneva',
    lots: 200,
    flag: '🇨🇭',
  },
  {
    house: 'Antiquorum',
    event: { en: 'Important Modern & Vintage Timepieces', it: 'Orologi Moderni e Vintage Importanti' },
    date: '19 Jul 2026',
    location: 'Hong Kong',
    lots: 60,
    flag: '🇭🇰',
  },
]

const AUCTION_RESULTS = [
  {
    watch: 'Rolex "Paul Newman" Daytona 6241',
    house: "Christie's Geneva",
    date: 'May 2026',
    hammer: '€1.240.000',
    estimate: '€800.000–1.200.000',
    over: true,
  },
  {
    watch: 'Patek Philippe 5711/1A Nautilus (Final Series)',
    house: "Sotheby's NY",
    date: 'Apr 2026',
    hammer: '€340.000',
    estimate: '€200.000–280.000',
    over: true,
  },
  {
    watch: 'AP Royal Oak "Jumbo" 5402ST (1972)',
    house: 'Phillips Geneva',
    date: 'Apr 2026',
    hammer: '€285.000',
    estimate: '€220.000–300.000',
    over: false,
  },
  {
    watch: 'Rolex Submariner 6538 "James Bond"',
    house: "Christie's",
    date: 'Mar 2026',
    hammer: '€195.000',
    estimate: '€150.000–200.000',
    over: false,
  },
  {
    watch: 'Omega Speedmaster CK2998 Pre-Professional',
    house: 'Antiquorum',
    date: 'Mar 2026',
    hammer: '€62.000',
    estimate: '€45.000–70.000',
    over: false,
  },
]

const TOP_INVESTMENT = {
  brand: 'Patek Philippe',
  model: 'Nautilus 5711/1A',
  ref: '5711/1A',
  score: 91,
  return12m: '+18.4%',
  volume: '€12.3M/month',
  liquidity: { en: 'Very High', it: 'Molto Alta' },
  img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBp7dzlBZ8vMf5MXzjB9qO7znaZSe9eQ-tgvMyk-dnzitnte4kd7lOFWyez-dbfh9nmGjMZqrzMnOYpBKC9dLiAu6bKBFWVHwcMhywGDNpbbzblf6ucRt1rGaYa9NkuyiikrcwQAceKZY65PJy24XEBQAhWE6nf2wBsQN9lkSlXtl0-pw4OLhJml0wPp1bOub0mN-aXRz7VBOYieKFtWjzfRHHTyj2Spe7y3AIM_gLuMEvzRyZkbifH422LWp_uij3XO41Hg2admIg',
  trend: [180, 172, 178, 185, 190, 183, 195, 202, 208, 215, 218, 225],
  signal: { en: 'Strong Buy', it: 'Forte Acquisto' },
  analysis: {
    en: 'The 5711/1A remains the most liquid steel sport watch in the secondary market. Discontinuation in 2022 created structural scarcity — production ceased at ~1,600 units/year. Institutional demand from family offices and US collectors continues to absorb supply at elevated premiums.',
    it: 'Il 5711/1A rimane l\'orologio sportivo in acciaio più liquido nel mercato secondario. L\'interruzione nel 2022 ha creato una scarsità strutturale — produzione cessata a ~1.600 pezzi/anno. La domanda istituzionale da family office e collezionisti USA continua ad assorbire l\'offerta a premi elevati.',
  },
}

// Recent searches stored in sessionStorage
function getRecentSearches(): { ref: string; ts: number }[] {
  try {
    return JSON.parse(sessionStorage.getItem('recentSearches') || '[]')
  } catch { return [] }
}

// ── Trend sparkline ───────────────────────────────────────────────────────────
function Sparkline({ values, color = '#f2c345' }: { values: number[]; color?: string }) {
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const w = 280
  const h = 60
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * w
    const y = h - ((v - min) / range) * (h - 8) - 4
    return `${x},${y}`
  }).join(' ')
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full" preserveAspectRatio="none">
      <defs>
        <linearGradient id="spGrad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <polygon points={`0,${h} ${pts} ${w},${h}`} fill="url(#spGrad)" />
    </svg>
  )
}

// ── Market Intelligence types ─────────────────────────────────────────────────
interface IntelCard {
  reference: string
  brand: string
  model: string
  has_data?: boolean
}
interface AppreciationCard extends IntelCard {
  current_price_chf: number
  price_6m_ago_chf: number
  change_pct: number
  period_days: number
  listings_count: number
  sparkline: number[]
}
interface OfferedCard extends IntelCard {
  listings_count: number
  current_price_chf: number
  change_pct_6m?: number
  supply_note: string       // Italian
  supply_note_en?: string   // English
}
interface RarestCard extends IntelCard {
  listings_count: number
  current_price_chf: number
  change_pct_6m?: number
  scarcity_note: string       // Italian
  scarcity_note_en?: string   // English
}
interface MarketIntelligence {
  most_appreciated: AppreciationCard
  most_offered: OfferedCard
  rarest: RarestCard
  computed_at: string
}

function useMarketIntelligence() {
  return useQuery<MarketIntelligence>({
    queryKey: ['market-intelligence'],
    queryFn: () =>
      fetch('/api/market/intelligence')
        .then(r => { if (!r.ok) throw new Error('api error'); return r.json() }),
    retry: false,
    staleTime: 15 * 60 * 1000,
  })
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function HomePage() {
  const navigate = useNavigate()
  const { t, lang } = useLang()
  const recentSearches = getRecentSearches()

  const months = lang === 'it'
    ? ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic']
    : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

  // ── Market Intelligence (single endpoint, 3 dynamic cards) ──────────────
  const { data: intel, isLoading: intelLoading } = useMarketIntelligence()

  // ── News query ────────────────────────────────────────────────────────────
  const { data: newsData } = useQuery({
    queryKey: ['news'],
    queryFn: () =>
      fetch('/api/news?limit=6')
        .then(r => { if (!r.ok) throw new Error('api error'); return r.json() }),
    retry: false,
    staleTime: 10 * 60 * 1000,
  })

  // ── Auction upcoming query (with mock fallback) ───────────────────────────
  const { data: upcomingData } = useQuery({
    queryKey: ['auctions-upcoming'],
    queryFn: () =>
      fetch('/api/auctions/upcoming')
        .then(r => { if (!r.ok) throw new Error('api error'); return r.json() }),
    retry: false,
    staleTime: 30 * 60 * 1000,
  })

  // Normalize API auctions (sale_name:string) → template format (event:{en,it})
  const auctionCalendar: typeof AUCTION_CALENDAR =
    upcomingData?.auctions?.length
      ? upcomingData.auctions.map((a: Record<string, unknown>) => ({
          house: a.house as string,
          event: a.event ?? { en: a.sale_name as string, it: a.sale_name as string },
          date: (() => {
            const raw = a.date as string | undefined
            if (!raw) return '—'
            try {
              const d = new Date(raw)
              return d.toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
            } catch { return raw }
          })(),
          location: a.location as string ?? '—',
          lots: (a.lots as number) ?? 0,
          flag: a.flag as string ?? (
            (a.location as string)?.toLowerCase().includes('hong kong') ? '🇭🇰' :
            (a.location as string)?.toLowerCase().includes('geneva') || (a.location as string)?.toLowerCase().includes('ginevra') ? '🇨🇭' :
            (a.location as string)?.toLowerCase().includes('new york') ? '🇺🇸' :
            (a.location as string)?.toLowerCase().includes('london') || (a.location as string)?.toLowerCase().includes('londra') ? '🇬🇧' :
            (a.location as string)?.toLowerCase().includes('paris') || (a.location as string)?.toLowerCase().includes('parigi') ? '🇫🇷' :
            (a.location as string)?.toLowerCase().includes('monaco') ? '🇲🇨' :
            (a.location as string)?.toLowerCase().includes('milan') || (a.location as string)?.toLowerCase().includes('milano') ? '🇮🇹' :
            (a.location as string)?.toLowerCase().includes('torino') ? '🇮🇹' : '🌍'
          ),
        }))
      : AUCTION_CALENDAR

  const newsItems: Array<{
    title: string
    summary?: string
    url: string
    image_url?: string
    source?: string
    published_at?: string
    tags?: string[]
  }> = newsData?.news ?? []

  return (
    <main className="p-8 max-w-[1600px] mx-auto space-y-[32px]">

      {/* ── 1. Market Intelligence ────────────────────────────────────────── */}
      <section>
        <div className="flex justify-between items-baseline mb-6">
          <div>
            <h2 className="font-h1 text-h1 text-zinc-100">
              {lang === 'it' ? 'Segnali di Mercato' : 'Market Signals'}
            </h2>
            <p className="text-zinc-500 text-sm mt-1">
              {lang === 'it'
                ? 'Dati live: apprezzamento, liquidità e scarsità nel mercato secondario'
                : 'Live data: appreciation, liquidity and scarcity in the secondary market'}
            </p>
          </div>
          {intel?.computed_at && (
            <span className="text-zinc-600 text-[10px] font-mono-data hidden md:block">
              {lang === 'it' ? 'Aggiornato' : 'Updated'}{' '}
              {new Date(intel.computed_at).toLocaleTimeString(lang === 'it' ? 'it-IT' : 'en-GB', { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>

        {intelLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-[12px]">
            {[0, 1, 2].map(i => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 p-6 h-52 animate-pulse">
                <div className="h-3 bg-zinc-800 rounded w-1/3 mb-4" />
                <div className="h-5 bg-zinc-800 rounded w-2/3 mb-2" />
                <div className="h-8 bg-zinc-800 rounded w-1/2 mb-3" />
                <div className="h-3 bg-zinc-800 rounded w-full mb-1" />
                <div className="h-3 bg-zinc-800 rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : intel ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-[12px]">

            {/* ── Card 1: Maggior Apprezzamento ─────────────────────────── */}
            <div
              className="bg-zinc-900 border border-zinc-800 hover:border-green-500/40 transition-colors cursor-pointer group flex flex-col"
              onClick={() => navigate(`/search?ref=${encodeURIComponent(intel.most_appreciated.reference)}`)}
            >
              {/* Header */}
              <div className="px-5 pt-5 pb-4 border-b border-zinc-800">
                <div className="flex items-center justify-between mb-1">
                  <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-green-400">
                    <span className="material-symbols-outlined text-sm leading-none" style={{ fontVariationSettings: "'FILL' 1" }}>trending_up</span>
                    {lang === 'it' ? 'Maggior Apprezzamento' : 'Best Appreciation'}
                  </span>
                  <span className="bg-green-400/10 border border-green-400/20 text-green-400 text-[11px] font-bold px-2 py-0.5 font-mono-data">
                    +{intel.most_appreciated.change_pct.toFixed(1)}%
                  </span>
                </div>
                <p className="text-[10px] text-zinc-500 font-mono-data">
                  {lang === 'it' ? `Ultimi ${Math.round(intel.most_appreciated.period_days / 30)} mesi` : `Last ${Math.round(intel.most_appreciated.period_days / 30)} months`}
                </p>
              </div>

              {/* Body */}
              <div className="px-5 py-4 flex-1">
                <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-0.5">{intel.most_appreciated.brand}</p>
                <h3 className="font-['Space_Grotesk'] font-bold text-zinc-100 text-lg leading-tight mb-3">
                  {intel.most_appreciated.model}
                  <span className="ml-2 text-zinc-500 text-xs font-mono-data font-normal">{intel.most_appreciated.reference}</span>
                </h3>

                {/* Price evolution */}
                <div className="flex items-end gap-3 mb-3">
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-0.5">{lang === 'it' ? '6 mesi fa' : '6 months ago'}</p>
                    <p className="font-mono-data text-zinc-400 text-sm line-through">
                      CHF {intel.most_appreciated.price_6m_ago_chf.toLocaleString('it-CH', { maximumFractionDigits: 0 })}
                    </p>
                  </div>
                  <span className="material-symbols-outlined text-green-400 text-base mb-0.5">arrow_forward</span>
                  <div>
                    <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-0.5">{lang === 'it' ? 'Ora' : 'Now'}</p>
                    <p className="font-mono-data text-green-400 font-bold text-lg">
                      CHF {intel.most_appreciated.current_price_chf.toLocaleString('it-CH', { maximumFractionDigits: 0 })}
                    </p>
                  </div>
                </div>

                <p className="text-zinc-500 text-xs">
                  {intel.most_appreciated.listings_count} {lang === 'it' ? 'annunci attivi' : 'active listings'}
                </p>
              </div>

              {/* Sparkline footer */}
              {intel.most_appreciated.sparkline.length > 2 && (
                <div className="h-[48px] px-0 pb-0 mt-auto border-t border-zinc-800/50">
                  <Sparkline values={intel.most_appreciated.sparkline} color="#4ade80" />
                </div>
              )}
            </div>

            {/* ── Card 2: Più Offerto ────────────────────────────────────── */}
            <div
              className="bg-zinc-900 border border-zinc-800 hover:border-orange-500/40 transition-colors cursor-pointer group flex flex-col"
              onClick={() => navigate(`/search?ref=${encodeURIComponent(intel.most_offered.reference)}`)}
            >
              {/* Header */}
              <div className="px-5 pt-5 pb-4 border-b border-zinc-800">
                <div className="flex items-center justify-between mb-1">
                  <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-orange-400">
                    <span className="material-symbols-outlined text-sm leading-none" style={{ fontVariationSettings: "'FILL' 1" }}>inventory_2</span>
                    {lang === 'it' ? 'Più Offerto' : 'Highest Supply'}
                  </span>
                  <span className="bg-orange-400/10 border border-orange-400/20 text-orange-400 text-[11px] font-bold px-2 py-0.5 font-mono-data">
                    {intel.most_offered.listings_count} {lang === 'it' ? 'annunci' : 'listings'}
                  </span>
                </div>
                <p className="text-[10px] text-zinc-500 font-mono-data">
                  {lang === 'it' ? 'Mercato secondario globale' : 'Global secondary market'}
                </p>
              </div>

              {/* Body */}
              <div className="px-5 py-4 flex-1">
                <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-0.5">{intel.most_offered.brand}</p>
                <h3 className="font-['Space_Grotesk'] font-bold text-zinc-100 text-lg leading-tight mb-3">
                  {intel.most_offered.model}
                  <span className="ml-2 text-zinc-500 text-xs font-mono-data font-normal">{intel.most_offered.reference}</span>
                </h3>

                {/* Price + trend */}
                <div className="mb-3">
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-0.5">{lang === 'it' ? 'Prezzo mediana' : 'Median price'}</p>
                  <p className="font-mono-data text-orange-400 font-bold text-lg">
                    CHF {intel.most_offered.current_price_chf.toLocaleString('it-CH', { maximumFractionDigits: 0 })}
                  </p>
                  {intel.most_offered.change_pct_6m != null && (
                    <p className={`text-xs font-mono-data mt-0.5 ${intel.most_offered.change_pct_6m >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {intel.most_offered.change_pct_6m >= 0 ? '+' : ''}{intel.most_offered.change_pct_6m.toFixed(1)}%{' '}
                      <span className="text-zinc-500 font-normal">6M</span>
                    </p>
                  )}
                </div>

                {/* Supply note */}
                <p className="text-zinc-400 text-xs leading-relaxed">
                  {lang === 'it' ? intel.most_offered.supply_note : (intel.most_offered.supply_note_en ?? intel.most_offered.supply_note)}
                </p>
              </div>

              {/* Supply bar */}
              <div className="px-5 py-4 border-t border-zinc-800/50 mt-auto">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] text-zinc-600 uppercase tracking-widest">{lang === 'it' ? 'Offerta' : 'Supply'}</span>
                  <span className="text-[10px] text-orange-400 font-bold font-mono-data">
                    {Math.min(100, Math.round((intel.most_offered.listings_count / 150) * 100))}%
                  </span>
                </div>
                <div className="h-1 bg-zinc-800 w-full">
                  <div
                    className="h-full bg-orange-400 transition-all duration-700"
                    style={{ width: `${Math.min(100, Math.max(5, Math.round((intel.most_offered.listings_count / 150) * 100)))}%` }}
                  />
                </div>
              </div>
            </div>

            {/* ── Card 3: Più Raro ──────────────────────────────────────── */}
            <div
              className="bg-zinc-900 border border-zinc-800 hover:border-blue-500/40 transition-colors cursor-pointer group flex flex-col"
              onClick={() => navigate(`/search?ref=${encodeURIComponent(intel.rarest.reference)}`)}
            >
              {/* Header */}
              <div className="px-5 pt-5 pb-4 border-b border-zinc-800">
                <div className="flex items-center justify-between mb-1">
                  <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-blue-400">
                    <span className="material-symbols-outlined text-sm leading-none" style={{ fontVariationSettings: "'FILL' 1" }}>diamond</span>
                    {lang === 'it' ? 'Più Raro' : 'Rarest'}
                  </span>
                  <span className="bg-blue-400/10 border border-blue-400/20 text-blue-400 text-[11px] font-bold px-2 py-0.5 font-mono-data">
                    {intel.rarest.listings_count} {lang === 'it' ? 'annunci' : 'listings'}
                  </span>
                </div>
                <p className="text-[10px] text-zinc-500 font-mono-data">
                  {lang === 'it' ? 'Mercato secondario globale' : 'Global secondary market'}
                </p>
              </div>

              {/* Body */}
              <div className="px-5 py-4 flex-1">
                <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-0.5">{intel.rarest.brand}</p>
                <h3 className="font-['Space_Grotesk'] font-bold text-zinc-100 text-lg leading-tight mb-3">
                  {intel.rarest.model}
                  <span className="ml-2 text-zinc-500 text-xs font-mono-data font-normal">{intel.rarest.reference}</span>
                </h3>

                {/* Price */}
                <div className="mb-3">
                  <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-0.5">{lang === 'it' ? 'Prezzo mediana' : 'Median price'}</p>
                  <p className="font-mono-data text-blue-400 font-bold text-lg">
                    CHF {intel.rarest.current_price_chf.toLocaleString('it-CH', { maximumFractionDigits: 0 })}
                  </p>
                  {intel.rarest.change_pct_6m != null && (
                    <p className={`text-xs font-mono-data mt-0.5 ${intel.rarest.change_pct_6m >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {intel.rarest.change_pct_6m >= 0 ? '+' : ''}{intel.rarest.change_pct_6m.toFixed(1)}%{' '}
                      <span className="text-zinc-500 font-normal">6M</span>
                    </p>
                  )}
                </div>

                {/* Scarcity note */}
                <p className="text-zinc-400 text-xs leading-relaxed">
                  {lang === 'it' ? intel.rarest.scarcity_note : (intel.rarest.scarcity_note_en ?? intel.rarest.scarcity_note)}
                </p>
              </div>

              {/* Scarcity bar */}
              <div className="px-5 py-4 border-t border-zinc-800/50 mt-auto">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] text-zinc-600 uppercase tracking-widest">{lang === 'it' ? 'Scarsità' : 'Scarcity'}</span>
                  <span className="text-[10px] text-blue-400 font-bold font-mono-data">
                    {Math.max(0, Math.min(100, Math.round(100 - (intel.rarest.listings_count / 150) * 100)))}%
                  </span>
                </div>
                <div className="h-1 bg-zinc-800 w-full">
                  <div
                    className="h-full bg-blue-400 transition-all duration-700"
                    style={{ width: `${Math.max(5, Math.min(100, Math.round(100 - (intel.rarest.listings_count / 150) * 100)))}%` }}
                  />
                </div>
              </div>
            </div>

          </div>
        ) : (
          /* Fallback se API non disponibile */
          <div className="bg-zinc-900 border border-zinc-800 p-6 text-center">
            <span className="material-symbols-outlined text-zinc-600 text-3xl mb-2 block">bar_chart</span>
            <p className="text-zinc-500 text-sm">
              {lang === 'it' ? 'Dati di mercato in aggiornamento…' : 'Market data updating…'}
            </p>
          </div>
        )}
      </section>

      {/* ── 2. Auction Calendar ──────────────────────────────────────────── */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-h2 text-h2 text-zinc-100">{t.auctionCalendarTitle}</h2>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3">{t.auction_house}</th>
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3 hidden md:table-cell">Event</th>
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3">{t.auction_date}</th>
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3 hidden sm:table-cell">{t.auction_location}</th>
                <th className="text-right text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3">{t.auction_lots}</th>
              </tr>
            </thead>
            <tbody>
              {auctionCalendar.map((a, i) => (
                <tr
                  key={i}
                  className="border-b border-zinc-800/50 last:border-0 hover:bg-zinc-800/30 transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <span className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-sm">{a.house}</span>
                  </td>
                  <td className="px-6 py-4 hidden md:table-cell">
                    <span className="text-zinc-400 text-xs">{a.event[lang]}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono-data text-yellow-400 text-xs">{a.date}</span>
                  </td>
                  <td className="px-6 py-4 hidden sm:table-cell">
                    <span className="text-zinc-400 text-xs flex items-center gap-1.5">
                      <span>{a.flag}</span>
                      {a.location}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono-data text-zinc-300 text-xs">{a.lots} lots</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── 3. Latest Auction Results ────────────────────────────────────── */}
      <section>
        <div className="flex justify-between items-baseline mb-6">
          <div>
            <h2 className="font-h2 text-h2 text-zinc-100">{t.auctionResultsTitle}</h2>
            <p className="text-zinc-500 text-sm mt-1">{t.auctionResultsSub}</p>
          </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3">Watch</th>
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3 hidden md:table-cell">{t.auction_house}</th>
                <th className="text-left text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3 hidden sm:table-cell">{t.auction_date}</th>
                <th className="text-right text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3">{t.auction_hammer}</th>
                <th className="text-right text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3 hidden lg:table-cell">{t.auction_estimate}</th>
                <th className="text-right text-[10px] font-label-caps text-zinc-500 uppercase px-6 py-3">{t.auction_result}</th>
              </tr>
            </thead>
            <tbody>
              {AUCTION_RESULTS.map((r, i) => (
                <tr key={i} className="border-b border-zinc-800/50 last:border-0 hover:bg-zinc-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {i === 0 && (
                        <span className="material-symbols-outlined text-yellow-400 text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                      )}
                      <span className="font-['Space_Grotesk'] font-medium text-zinc-100 text-sm">{r.watch}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 hidden md:table-cell">
                    <span className="text-zinc-400 text-xs">{r.house}</span>
                  </td>
                  <td className="px-6 py-4 hidden sm:table-cell">
                    <span className="text-zinc-500 text-xs">{r.date}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono-data text-yellow-400 font-semibold">{r.hammer}</span>
                  </td>
                  <td className="px-6 py-4 text-right hidden lg:table-cell">
                    <span className="font-mono-data text-zinc-500 text-xs">{r.estimate}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {r.over ? (
                      <span className="flex items-center justify-end gap-1 text-green-400 text-[10px] font-bold uppercase">
                        <span className="material-symbols-outlined text-sm leading-none">arrow_upward</span>
                        {t.priceUp}
                      </span>
                    ) : (
                      <span className="text-zinc-500 text-[10px] uppercase">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── 4. Top Investment Pick ───────────────────────────────────────── */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="font-h2 text-h2 text-zinc-100">{t.topInvestmentTitle}</h2>
            <p className="text-zinc-500 text-sm mt-1">{t.topInvestmentSub}</p>
          </div>
          <button
            onClick={() => navigate(`/search?ref=${encodeURIComponent(TOP_INVESTMENT.ref)}`)}
            className="text-xs text-yellow-400 uppercase tracking-widest font-bold hover:underline"
          >
            {t.searchNow}
          </button>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* Left: image + score */}
            <div className="flex flex-col gap-4">
              <div className="relative h-56 bg-zinc-950 border border-zinc-800 overflow-hidden">
                <img src={TOP_INVESTMENT.img} alt={TOP_INVESTMENT.model} className="w-full h-full object-cover" />
                <div className="absolute bottom-3 left-3 bg-primary text-on-primary text-[10px] font-bold px-2 py-1 uppercase tracking-tighter">
                  {TOP_INVESTMENT.signal[lang]}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-zinc-950 border border-zinc-800 p-3">
                  <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">{t.invest_score}</p>
                  <p className="font-['Space_Grotesk'] font-bold text-yellow-400 text-2xl">{TOP_INVESTMENT.score}</p>
                </div>
                <div className="bg-zinc-950 border border-zinc-800 p-3">
                  <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">{t.invest_12m}</p>
                  <p className="font-['Space_Grotesk'] font-bold text-green-400 text-2xl">{TOP_INVESTMENT.return12m}</p>
                </div>
                <div className="bg-zinc-950 border border-zinc-800 p-3">
                  <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">{t.invest_volume}</p>
                  <p className="font-mono-data text-zinc-300 text-sm">{TOP_INVESTMENT.volume}</p>
                </div>
                <div className="bg-zinc-950 border border-zinc-800 p-3">
                  <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">{t.invest_liquidity}</p>
                  <p className="font-mono-data text-green-400 text-sm">{TOP_INVESTMENT.liquidity[lang]}</p>
                </div>
              </div>
            </div>

            {/* Center: title + analysis */}
            <div className="flex flex-col justify-between gap-4">
              <div>
                <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">{TOP_INVESTMENT.brand}</p>
                <h3 className="font-['Space_Grotesk'] font-bold text-zinc-100 text-2xl mb-4">{TOP_INVESTMENT.model}</h3>
                <p className="text-zinc-400 text-sm leading-relaxed">{TOP_INVESTMENT.analysis[lang]}</p>
              </div>
            </div>

            {/* Right: sparkline chart */}
            <div className="flex flex-col gap-4">
              <div className="flex justify-between items-baseline">
                <span className="text-[10px] font-label-caps text-zinc-500 uppercase">12M Price Trend</span>
                <span className="text-green-400 text-xs font-bold">{TOP_INVESTMENT.return12m}</span>
              </div>
              <div className="h-[120px] relative">
                <Sparkline values={TOP_INVESTMENT.trend} />
              </div>
              <div className="flex justify-between text-[10px] text-zinc-600 font-mono-data uppercase">
                {[months[0], months[3], months[6], months[9], months[11]].map(m => (
                  <span key={m}>{m}</span>
                ))}
              </div>
              <div className="border-t border-zinc-800 pt-4 space-y-2">
                {[
                  { label: 'Jan 2025', value: `€${(TOP_INVESTMENT.trend[0] * 900).toLocaleString()}` },
                  { label: lang === 'it' ? 'Ora' : 'Now', value: `€${(TOP_INVESTMENT.trend[11] * 900).toLocaleString()}`, highlight: true },
                ].map(row => (
                  <div key={row.label} className="flex justify-between items-center text-xs">
                    <span className="text-zinc-500">{row.label}</span>
                    <span className={row.highlight ? 'text-yellow-400 font-bold font-mono-data' : 'text-zinc-400 font-mono-data'}>{row.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 5. Recent Searches ───────────────────────────────────────────── */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="font-h2 text-h2 text-zinc-100">{t.recentSearchesTitle}</h2>
            <p className="text-zinc-500 text-sm mt-1">{t.recentSearchesSub}</p>
          </div>
          <button
            onClick={() => navigate('/search')}
            className="text-xs text-yellow-400 uppercase tracking-widest font-bold hover:underline"
          >
            {t.searchNow}
          </button>
        </div>

        {recentSearches.length === 0 ? (
          <div className="bg-zinc-900 border border-zinc-800 border-dashed p-12 flex flex-col items-center justify-center text-center">
            <span className="material-symbols-outlined text-4xl text-zinc-700 mb-3">manage_search</span>
            <p className="font-['Space_Grotesk'] font-semibold text-zinc-400 text-sm">{t.noRecentSearches}</p>
            <p className="text-xs text-zinc-600 mt-1">{t.noRecentSub}</p>
            <button
              onClick={() => navigate('/search')}
              className="mt-4 bg-primary text-on-primary text-xs font-bold uppercase tracking-widest px-4 py-2 hover:opacity-90 transition-opacity"
            >
              {t.searchNow}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-[12px]">
            {recentSearches.slice(0, 8).map(s => (
              <div
                key={s.ref}
                onClick={() => navigate(`/search?ref=${encodeURIComponent(s.ref)}`)}
                className="bg-zinc-900 border border-zinc-800 p-4 cursor-pointer hover:border-zinc-700 transition-colors group"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="font-['Space_Grotesk'] font-bold text-zinc-100">{s.ref}</span>
                  <span className="material-symbols-outlined text-zinc-600 group-hover:text-yellow-400 transition-colors text-sm">open_in_new</span>
                </div>
                <p className="text-[10px] text-zinc-600 uppercase tracking-widest">
                  {new Date(s.ts).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── 6. Market News ───────────────────────────────────────────────── */}
      {newsData !== undefined && (
        <section>
          <div className="flex justify-between items-baseline mb-6">
            <div>
              <h2 className="font-h2 text-h2 text-zinc-100">
                {lang === 'it' ? 'Notizie dal Mercato' : 'Market News'}
              </h2>
              <p className="text-zinc-500 text-sm mt-1">
                {lang === 'it' ? 'Ultime dal mondo degli orologi' : 'Latest from the watch world'}
              </p>
            </div>
          </div>

          {newsItems.length === 0 ? (
            <div className="bg-zinc-900 border border-zinc-800 border-dashed p-12 flex flex-col items-center justify-center text-center">
              <span className="material-symbols-outlined text-4xl text-zinc-700 mb-3">newspaper</span>
              <p className="font-['Space_Grotesk'] font-semibold text-zinc-400 text-sm">
                {lang === 'it'
                  ? 'Notizie in caricamento... Il feed RSS si aggiorna ogni 12 ore.'
                  : 'News loading... The RSS feed updates every 12 hours.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[12px]">
              {newsItems.map((item, i) => {
                const pubDate = item.published_at
                  ? new Date(item.published_at).toLocaleDateString(
                      lang === 'it' ? 'it-IT' : 'en-GB',
                      { day: 'numeric', month: 'short', year: 'numeric' }
                    )
                  : null

                return (
                  <a
                    key={i}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-zinc-900 border border-zinc-800 flex flex-col hover:border-zinc-700 transition-colors group"
                  >
                    {/* Image */}
                    <div className="relative h-40 bg-zinc-950 overflow-hidden flex-shrink-0">
                      {item.image_url ? (
                        <img
                          src={item.image_url}
                          alt={item.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <span className="material-symbols-outlined text-5xl text-zinc-800">newspaper</span>
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="p-4 flex flex-col gap-2 flex-1">
                      {/* Source badge + date */}
                      <div className="flex items-center justify-between gap-2">
                        {item.source && (
                          <span className="text-[9px] font-bold uppercase tracking-widest bg-yellow-400/10 text-yellow-400 border border-yellow-400/20 px-2 py-0.5">
                            {item.source}
                          </span>
                        )}
                        {pubDate && (
                          <span className="text-[10px] text-zinc-600 font-mono-data ml-auto">{pubDate}</span>
                        )}
                      </div>

                      {/* Title */}
                      <h3 className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-sm leading-snug line-clamp-2">
                        {item.title}
                      </h3>

                      {/* Summary */}
                      {item.summary && (
                        <p className="text-zinc-400 text-xs leading-relaxed line-clamp-3 flex-1">
                          {item.summary}
                        </p>
                      )}

                      {/* Read more */}
                      <div className="flex items-center gap-1 mt-auto pt-2">
                        <span className="text-[10px] text-zinc-600 uppercase tracking-widest group-hover:text-yellow-400 transition-colors">
                          {lang === 'it' ? 'Leggi' : 'Read'}
                        </span>
                        <span className="material-symbols-outlined text-zinc-600 group-hover:text-yellow-400 transition-colors text-xs">open_in_new</span>
                      </div>
                    </div>
                  </a>
                )
              })}
            </div>
          )}
        </section>
      )}

    </main>
  )
}
