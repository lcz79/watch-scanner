import { useNavigate } from 'react-router-dom'
import { useLang } from '../lib/lang'

// ── Mock data ────────────────────────────────────────────────────────────────

const MARKET_HIGHLIGHTS = [
  {
    icon: 'trending_up',
    title: { en: 'Vintage Rolex', it: 'Rolex Vintage' },
    body: {
      en: 'Paul Newman Daytonas and Submariner MK1 dials continue commanding 20–35% premiums over 2024 highs.',
      it: 'I Paul Newman Daytona e i quadranti Submariner MK1 continuano a raggiungere premi del 20–35% rispetto ai massimi del 2024.',
    },
    tag: { en: 'Trending', it: 'In Rialzo' },
    tagColor: 'bg-green-400/10 text-green-400 border-green-400/20',
  },
  {
    icon: 'query_stats',
    title: { en: 'AP Royal Oak Correction', it: 'Correzione AP Royal Oak' },
    body: {
      en: 'Steel 15500ST stabilising around €40–44k after the 2023 peak. Considered a prime accumulation window.',
      it: 'Il 15500ST in acciaio si stabilizza attorno a €40–44k dopo il picco del 2023. Considerata una finestra di accumulo.',
    },
    tag: { en: 'Accumulate', it: 'Accumulo' },
    tagColor: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20',
  },
  {
    icon: 'new_releases',
    title: { en: 'Patek Nautilus Demand', it: 'Domanda Patek Nautilus' },
    body: {
      en: '5726A sky moon tourbillon breaks €500k private sales ceiling. Steel 5711/1A waitlist exceeds 8 years.',
      it: 'Il 5726A sky moon tourbillon supera i €500k nelle vendite private. Lista d\'attesa 5711/1A supera 8 anni.',
    },
    tag: { en: 'High Demand', it: 'Alta Domanda' },
    tagColor: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
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

// ── Component ─────────────────────────────────────────────────────────────────
export default function HomePage() {
  const navigate = useNavigate()
  const { t, lang } = useLang()
  const recentSearches = getRecentSearches()

  const months = lang === 'it'
    ? ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic']
    : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

  return (
    <main className="p-8 max-w-[1600px] mx-auto space-y-[32px]">

      {/* ── 1. Market Highlights ──────────────────────────────────────────── */}
      <section>
        <div className="flex justify-between items-baseline mb-6">
          <div>
            <h2 className="font-h1 text-h1 text-zinc-100">{t.watchWorldTitle}</h2>
            <p className="text-zinc-500 text-sm mt-1">{t.watchWorldSub}</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-[12px]">
          {MARKET_HIGHLIGHTS.map((h, i) => (
            <div key={i} className="bg-zinc-900 border border-zinc-800 p-6 flex flex-col gap-4 hover:border-zinc-700 transition-colors">
              <div className="flex justify-between items-start">
                <span className="material-symbols-outlined text-yellow-400 text-2xl">{h.icon}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 border uppercase tracking-widest ${h.tagColor}`}>
                  {h.tag[lang]}
                </span>
              </div>
              <div>
                <h3 className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-base mb-2">{h.title[lang]}</h3>
                <p className="text-zinc-400 text-xs leading-relaxed">{h.body[lang]}</p>
              </div>
            </div>
          ))}
        </div>
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
              {AUCTION_CALENDAR.map((a, i) => (
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

    </main>
  )
}
