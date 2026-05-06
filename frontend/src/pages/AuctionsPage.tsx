import { useState, useEffect } from 'react'
import { useLang } from '../lib/lang'

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

const HOUSES = [
  { id: 'christies', name: "Christie's",       url: 'christies.com',   loc: 'Geneva · New York · Hong Kong', status: 'active' as const, ago: '2h',  specialty: 'Important Watches — May & Nov' },
  { id: 'phillips',  name: 'Phillips',          url: 'phillips.com',    loc: 'Geneva · New York · Hong Kong', status: 'active' as const, ago: '1h',  specialty: 'Watches — May & Nov + Online' },
  { id: 'sothebys',  name: "Sotheby's",         url: 'sothebys.com',    loc: 'Geneva · London · New York',    status: 'active' as const, ago: '3h',  specialty: 'Important Watches — May & Nov' },
  { id: 'antiquorum',name: 'Antiquorum',        url: 'antiquorum.com',  loc: 'Geneva · Hong Kong',            status: 'active' as const, ago: '5h',  specialty: 'Modern & Vintage Timepieces' },
  { id: 'artcurial', name: 'Artcurial',         url: 'artcurial.com',   loc: 'Paris · Monaco',                status: 'active' as const, ago: '6h',  specialty: 'Montres de Collection' },
  { id: 'bonhams',   name: 'Bonhams',           url: 'bonhams.com',     loc: 'London · Los Angeles',          status: 'pending' as const, ago: '—', specialty: 'Watches & Clocks' },
  { id: 'dorotheum', name: 'Dorotheum',         url: 'dorotheum.com',   loc: 'Vienna · Prague',               status: 'pending' as const, ago: '—', specialty: 'Uhren & Taschenuhren' },
]

type Upcoming = {
  id: string; house: string; sale: { en: string; it: string }
  date: string; location: string; lots: number
  low: number; high: number; currency: string; isLive: boolean
}

const UPCOMING: Upcoming[] = [
  { id: '1', house: "Christie's",  sale: { en: 'The Geneva Watch Auction: Important Timepieces', it: 'Asta Ginevra: Orologi Importanti' }, date: '2026-05-12T14:00:00', location: 'Geneva',  lots: 182, low: 45_000_000, high: 65_000_000, currency: 'CHF', isLive: false },
  { id: '2', house: 'Phillips',    sale: { en: 'Watches Online: Spring 2026',                    it: 'Watches Online: Primavera 2026'   }, date: '2026-05-15T10:00:00', location: 'Online',  lots: 120, low:  8_000_000, high: 12_000_000, currency: 'CHF', isLive: false },
  { id: '3', house: "Sotheby's",   sale: { en: 'Important Watches',                              it: 'Orologi Importanti'               }, date: '2026-05-20T15:00:00', location: 'Geneva',  lots:  98, low: 30_000_000, high: 46_000_000, currency: 'CHF', isLive: false },
  { id: '4', house: 'Antiquorum',  sale: { en: 'Important Modern & Vintage Timepieces',          it: 'Segnatempo Moderni e Vintage'     }, date: '2026-06-01T14:00:00', location: 'Geneva',  lots: 205, low: 15_000_000, high: 25_000_000, currency: 'CHF', isLive: false },
  { id: '5', house: 'Artcurial',   sale: { en: 'Montres de Collection',                          it: 'Orologi da Collezione'            }, date: '2026-06-08T11:00:00', location: 'Paris',   lots: 148, low: 10_000_000, high: 18_000_000, currency: 'EUR', isLive: false },
  { id: '6', house: "Christie's",  sale: { en: 'Watches Online: Summer Edition',                 it: 'Watches Online: Edizione Estate'  }, date: '2026-06-20T10:00:00', location: 'Online',  lots:  88, low:  3_000_000, high:  6_000_000, currency: 'CHF', isLive: false },
]

type Lot = {
  id: string; house: string; lotNum: string; brand: string; ref: string
  desc: { en: string; it: string }; year: number
  sale: string; date: string; low: number; high: number; currency: string
}

const FEATURED_LOTS: Lot[] = [
  { id: '1', house: "Christie's",  lotNum: '12', brand: 'Patek Philippe',      ref: '5711/1A-010',       desc: { en: 'Nautilus stainless steel, slate dial, 2020',               it: 'Nautilus acciaio, quadrante ardesia, 2020'             }, year: 2020, sale: 'Geneva Watch Auction',    date: '12 May', low: 120_000, high: 180_000, currency: 'CHF' },
  { id: '2', house: 'Phillips',    lotNum: '34', brand: 'Rolex',               ref: '1665 "Double Red"', desc: { en: 'Sea-Dweller Double Red, rare Mk I, 1969',                  it: 'Sea-Dweller Doppio Rosso, raro Mk I, 1969'            }, year: 1969, sale: 'Watches Online Spring',   date: '15 May', low:  80_000, high: 140_000, currency: 'CHF' },
  { id: '3', house: "Sotheby's",   lotNum: '7',  brand: 'A. Lange & Söhne',   ref: 'Lange 1 Tourbillon',desc: { en: 'White gold, box and papers, 2015',                         it: 'Oro bianco, scatola e documenti, 2015'                }, year: 2015, sale: 'Important Watches',       date: '20 May', low: 200_000, high: 280_000, currency: 'CHF' },
  { id: '4', house: "Christie's",  lotNum: '28', brand: 'F.P. Journe',         ref: 'Tourbillon Souverain',desc:{ en: 'Platinum, argenté dial, first series, 2001',               it: 'Platino, quadrante argenté, prima serie, 2001'        }, year: 2001, sale: 'Geneva Watch Auction',    date: '12 May', low: 350_000, high: 500_000, currency: 'CHF' },
  { id: '5', house: 'Antiquorum',  lotNum: '89', brand: 'Rolex',               ref: '6241 "Paul Newman"', desc: { en: 'Daytona exotic dial, excellent condition, 1968',            it: 'Daytona quadrante esotico, ottime condizioni, 1968'    }, year: 1968, sale: 'Important Vintage',       date: '1 Jun',  low: 180_000, high: 260_000, currency: 'CHF' },
  { id: '6', house: 'Phillips',    lotNum: '56', brand: 'Patek Philippe',      ref: '2499 4th Series',   desc: { en: 'Perpetual cal. chronograph, pink gold, 1982',             it: 'Calendario perpetuo cronografo, oro rosa, 1982'       }, year: 1982, sale: 'Geneva Watch Auction',    date: '12 May', low: 400_000, high: 700_000, currency: 'CHF' },
]

type Record = { brand: string; ref: string; house: string; date: string; estimate: number; hammer: number; currency: string }

const RECORDS: Record[] = [
  { brand: 'Rolex',              ref: '6239 "Paul Newman"',         house: 'Phillips',    date: 'Oct 2017', estimate:  1_000_000, hammer: 17_752_500, currency: 'USD' },
  { brand: 'Patek Philippe',     ref: '1518 Stainless Steel',       house: "Christie's",  date: 'Nov 2016', estimate:    500_000, hammer: 11_112_020, currency: 'CHF' },
  { brand: 'Patek Philippe',     ref: '5271P Perpetual Calendar',   house: 'Phillips',    date: 'May 2022', estimate:  4_000_000, hammer:  7_000_000, currency: 'CHF' },
  { brand: 'Patek Philippe',     ref: '2499/100',                   house: "Sotheby's",   date: 'May 2023', estimate:  3_000_000, hammer:  5_500_000, currency: 'CHF' },
  { brand: 'Rolex',              ref: '6265 Daytona "Oyster"',      house: 'Antiquorum',  date: 'Nov 2020', estimate:    150_000, hammer:  3_500_000, currency: 'CHF' },
  { brand: 'Richard Mille',      ref: 'RM 56-02 Sapphire',         house: "Christie's",  date: 'Nov 2021', estimate:  1_200_000, hammer:  2_900_000, currency: 'HKD' },
  { brand: 'Vacheron Constantin',ref: 'Grande Complication 57260',  house: "Christie's",  date: 'Nov 2015', estimate:    800_000, hammer:  2_300_000, currency: 'CHF' },
  { brand: 'F.P. Journe',        ref: 'Resonance Platinum',        house: "Sotheby's",   date: 'May 2021', estimate:  1_000_000, hammer:  2_100_000, currency: 'CHF' },
  { brand: 'Audemars Piguet',    ref: '5516 Grande Complication',  house: "Christie's",  date: 'May 2019', estimate:    900_000, hammer:  1_850_000, currency: 'CHF' },
  { brand: 'Rolex',              ref: '6263 "Oyster Sotto"',        house: 'Phillips',    date: 'Nov 2019', estimate:    200_000, hammer:  1_650_000, currency: 'CHF' },
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtM(n: number, cur: string) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M ${cur}`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K ${cur}`
  return `${n.toLocaleString()} ${cur}`
}

function fmtDate(iso: string, lang: string) {
  return new Date(iso).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short' })
}

function useCountdown(targetISO: string) {
  const [diff, setDiff] = useState(0)
  useEffect(() => {
    const update = () => setDiff(Math.max(0, new Date(targetISO).getTime() - Date.now()))
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [targetISO])
  const d = Math.floor(diff / 86_400_000)
  const h = Math.floor((diff % 86_400_000) / 3_600_000)
  const m = Math.floor((diff % 3_600_000) / 60_000)
  const s = Math.floor((diff % 60_000) / 1_000)
  return { d, h, m, s, total: diff }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function CountdownBlock({ targetISO }: { targetISO: string }) {
  const { t } = useLang()
  const { d, h, m, s } = useCountdown(targetISO)
  return (
    <div className="flex items-center gap-3">
      {[
        { val: d,  label: d === 1 ? t.dayLabel : t.daysLabel },
        { val: h,  label: t.hoursLabel },
        { val: m,  label: t.minutesLabel },
        { val: s,  label: 's' },
      ].map(({ val, label }) => (
        <div key={label} className="text-center">
          <p className="font-display-price text-2xl text-primary leading-none">{String(val).padStart(2, '0')}</p>
          <p className="font-mono-data text-[9px] text-zinc-500 uppercase mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function AuctionsPage() {
  const { t, lang } = useLang()
  const [houseFilter, setHouseFilter] = useState<string>('all')
  const [sortField, setSortField] = useState<'hammer' | 'estimate'>('hammer')

  const nextAuction = UPCOMING.find(a => !a.isLive) ?? UPCOMING[0]
  const liveAuctions = UPCOMING.filter(a => a.isLive)

  const filteredLots = houseFilter === 'all'
    ? FEATURED_LOTS
    : FEATURED_LOTS.filter(l => l.house.toLowerCase().includes(houseFilter))

  const sortedRecords = [...RECORDS].sort((a, b) => b[sortField] - a[sortField])

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-10">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-end justify-between">
        <div>
          <span className="font-label-caps text-primary text-[10px] uppercase tracking-[0.2em] mb-2 block">
            {t.surveillanceLabel}
          </span>
          <h1 className="font-h1 text-on-surface text-3xl">{t.auctionIntelligence}</h1>
          <p className="text-zinc-500 text-sm mt-1 max-w-xl">{t.auctionIntelligenceSub}</p>
        </div>
        <div className="flex items-center gap-8">
          {/* KPIs */}
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">{t.housesConnected}</p>
            <p className="font-display-price text-2xl text-primary">
              {HOUSES.filter(h => h.status === 'active').length}
              <span className="text-zinc-600 text-sm">/{HOUSES.length}</span>
            </p>
          </div>
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">{t.totalLots}</p>
            <p className="font-display-price text-2xl text-primary">
              {UPCOMING.reduce((s, a) => s + a.lots, 0).toLocaleString()}
            </p>
          </div>
          {/* Live badge or countdown */}
          {liveAuctions.length > 0 ? (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 px-4 py-2 rounded">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <span className="font-label-caps text-xs text-red-400 uppercase">{t.liveNow}</span>
            </div>
          ) : (
            <div className="bg-zinc-900 border border-zinc-800 px-5 py-3 rounded">
              <p className="font-mono-data text-[9px] text-zinc-500 uppercase mb-2">{t.nextAuction}</p>
              <CountdownBlock targetISO={nextAuction.date} />
            </div>
          )}
        </div>
      </div>

      {/* ── Main grid ──────────────────────────────────────────── */}
      <div className="grid grid-cols-12 gap-8">

        {/* ── Left column ──────────────────────────── */}
        <div className="col-span-12 lg:col-span-4 space-y-6">

          {/* Upcoming calendar */}
          <section className="bg-zinc-900 border border-zinc-800">
            <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="font-h2 text-sm uppercase tracking-tight">{t.auctionCalendarTitle}</h3>
              <span className="font-mono-data text-[10px] text-zinc-500">{UPCOMING.length} {t.saleLabel.toLowerCase()}s</span>
            </div>
            <div className="divide-y divide-zinc-800">
              {UPCOMING.map(a => (
                <div key={a.id} className="px-5 py-4 hover:bg-zinc-800/40 transition-colors group">
                  <div className="flex items-start justify-between mb-1">
                    <span className="font-label-caps text-[9px] text-primary uppercase tracking-widest">{a.house}</span>
                    {a.isLive && (
                      <span className="flex items-center gap-1 bg-red-500/10 text-red-400 text-[8px] font-bold px-2 py-0.5 rounded uppercase">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />{t.liveNow}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-zinc-200 leading-snug mb-2 group-hover:text-yellow-400 transition-colors">
                    {a.sale[lang]}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-zinc-500">
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-[12px]">calendar_today</span>
                      {fmtDate(a.date, lang)} · {a.location === 'Online' ? t.onlineLabel : a.location}
                    </span>
                    <span>{a.lots} {t.lotsLabel}</span>
                  </div>
                  <div className="mt-2 text-[10px] text-zinc-400">
                    <span className="text-zinc-600">{t.estimateLabel}: </span>
                    {fmtM(a.low, a.currency)} – {fmtM(a.high, a.currency)}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Connected sources */}
          <section className="bg-zinc-900 border border-zinc-800">
            <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="font-h2 text-sm uppercase tracking-tight">{t.connectedSources}</h3>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                <span className="font-mono-data text-[10px] text-green-400">{t.sourceActive}</span>
              </div>
            </div>

            {/* Scraping frequencies */}
            <div className="px-5 py-3 border-b border-zinc-800 bg-zinc-950/50 space-y-1.5">
              {[
                { icon: 'bolt',          label: t.scrapingLive },
                { icon: 'calendar_month',label: t.scrapingCalendar },
                { icon: 'task_alt',      label: t.scrapingResults },
              ].map(({ icon, label }) => (
                <div key={label} className="flex items-center gap-2 text-[10px] text-zinc-500">
                  <span className="material-symbols-outlined text-[12px] text-yellow-400">{icon}</span>
                  <span className="font-mono-data">{label}</span>
                </div>
              ))}
            </div>

            <div className="divide-y divide-zinc-800">
              {HOUSES.map(h => (
                <div key={h.id} className="px-5 py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${h.status === 'active' ? 'bg-green-500' : 'bg-zinc-600'}`} />
                      <p className="font-['Space_Grotesk'] text-sm text-zinc-200 truncate">{h.name}</p>
                    </div>
                    <p className="text-[10px] text-zinc-500 truncate pl-3.5">{h.loc}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className={`font-label-caps text-[9px] uppercase ${h.status === 'active' ? 'text-green-400' : 'text-zinc-600'}`}>
                      {h.status === 'active' ? t.sourceActive : t.sourcePending}
                    </p>
                    {h.ago !== '—' && (
                      <p className="font-mono-data text-[9px] text-zinc-600">{t.lastUpdatedLabel} {h.ago}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="px-5 py-3 border-t border-zinc-800 bg-zinc-950/30">
              <p className="text-[10px] text-zinc-600 leading-relaxed">
                {lang === 'it'
                  ? 'Integrazione via scraping HTML · Christie\'s · Sotheby\'s · Phillips · Antiquorum · Artcurial · Bonhams · Dorotheum'
                  : 'Data via HTML scraping · Christie\'s · Sotheby\'s · Phillips · Antiquorum · Artcurial · Bonhams · Dorotheum'}
              </p>
            </div>
          </section>
        </div>

        {/* ── Right column ─────────────────────────── */}
        <div className="col-span-12 lg:col-span-8 space-y-8">

          {/* Featured lots */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-h2 text-sm uppercase tracking-tight">{t.featuredLotsLabel}</h3>
              {/* House filter */}
              <div className="flex gap-1">
                {['all', 'christies', 'phillips', 'sothebys', 'antiquorum'].map(f => (
                  <button
                    key={f}
                    onClick={() => setHouseFilter(f)}
                    className={`px-2.5 py-1 text-[9px] font-bold uppercase tracking-widest rounded transition-colors ${
                      houseFilter === f
                        ? 'bg-primary text-zinc-950'
                        : 'bg-zinc-900 text-zinc-500 hover:text-zinc-200 border border-zinc-800'
                    }`}
                  >
                    {f === 'all' ? t.allHousesLabel
                      : f === 'christies' ? "Christie's"
                      : f === 'phillips'  ? 'Phillips'
                      : f === 'sothebys'  ? "Sotheby's"
                      : 'Antiquorum'}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredLots.map(lot => (
                <article key={lot.id} className="bg-zinc-900 border border-zinc-800 hover:border-primary/40 transition-colors group">
                  {/* Image placeholder */}
                  <div className="h-36 bg-zinc-950 border-b border-zinc-800 flex items-center justify-center relative overflow-hidden">
                    <span className="material-symbols-outlined text-5xl text-zinc-800 group-hover:text-zinc-700 transition-colors">watch</span>
                    <div className="absolute top-2 left-2 bg-zinc-950/90 px-2 py-0.5">
                      <span className="font-mono-data text-[9px] text-primary uppercase">{lot.house}</span>
                    </div>
                    <div className="absolute top-2 right-2 bg-zinc-950/90 px-2 py-0.5">
                      <span className="font-mono-data text-[9px] text-zinc-400">{t.lotLabel} {lot.lotNum}</span>
                    </div>
                  </div>

                  <div className="p-4">
                    <p className="font-label-caps text-[9px] text-zinc-500 uppercase mb-1">{lot.brand}</p>
                    <p className="font-['Space_Grotesk'] font-bold text-sm text-zinc-100 mb-1 leading-snug group-hover:text-yellow-400 transition-colors">
                      {lot.ref}
                    </p>
                    <p className="text-[11px] text-zinc-500 mb-3 leading-relaxed">
                      {lot.desc[lang]}
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-zinc-500 mb-3">
                      <span className="flex items-center gap-1">
                        <span className="material-symbols-outlined text-[11px]">calendar_today</span>
                        {lot.date} — {lot.sale}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-mono-data text-[9px] text-zinc-600 uppercase">{t.estimateLabel}</p>
                        <p className="font-mono-data text-sm text-zinc-200">
                          {fmtM(lot.low, '')}–{fmtM(lot.high, lot.currency)}
                        </p>
                      </div>
                      <button className="px-3 py-1.5 bg-primary/10 hover:bg-primary text-primary hover:text-zinc-950 text-[9px] font-bold uppercase tracking-widest transition-colors rounded">
                        {t.trackLotLabel}
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>

          {/* Record prices table */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-h2 text-sm uppercase tracking-tight">{t.recordPricesLabel}</h3>
              <div className="flex gap-1">
                {(['hammer', 'estimate'] as const).map(f => (
                  <button
                    key={f}
                    onClick={() => setSortField(f)}
                    className={`px-2.5 py-1 text-[9px] font-bold uppercase tracking-widest rounded transition-colors ${
                      sortField === f
                        ? 'bg-primary text-zinc-950'
                        : 'bg-zinc-900 text-zinc-500 hover:text-zinc-200 border border-zinc-800'
                    }`}
                  >
                    {f === 'hammer' ? t.hammerPriceLabel : t.estimateLabel}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 overflow-hidden">
              {/* Table header */}
              <div className="grid grid-cols-12 gap-3 px-4 py-2 border-b border-zinc-800 bg-zinc-950">
                {(['#', 'Reference', t.saleLabel, 'Date', t.estimateLabel, t.hammerPriceLabel, 'vs Est.']).map((h, i) => (
                  <div key={i} className={`font-label-caps text-[9px] text-zinc-600 uppercase ${
                    i === 0 ? 'col-span-1' : i === 1 ? 'col-span-3' : i === 2 ? 'col-span-2' : i === 3 ? 'col-span-1' : 'col-span-2'
                  }`}>{h}</div>
                ))}
              </div>

              {sortedRecords.map((r, i) => {
                const ratio = r.hammer / r.estimate
                const pct = ((ratio - 1) * 100).toFixed(0)
                const isHigh = ratio > 2
                return (
                  <div key={i} className="grid grid-cols-12 gap-3 px-4 py-3 border-b border-zinc-800 hover:bg-zinc-800/40 transition-colors items-center">
                    <div className="col-span-1 font-mono-data text-[11px] text-zinc-600">{String(i + 1).padStart(2, '0')}</div>
                    <div className="col-span-3">
                      <p className="text-xs text-zinc-200 font-['Space_Grotesk'] font-medium leading-tight">{r.ref}</p>
                      <p className="font-mono-data text-[9px] text-zinc-500">{r.brand}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="font-mono-data text-[10px] text-zinc-400">{r.house}</p>
                    </div>
                    <div className="col-span-1">
                      <p className="font-mono-data text-[10px] text-zinc-500">{r.date.split(' ')[1]}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="font-mono-data text-[11px] text-zinc-500">{fmtM(r.estimate, r.currency)}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="font-mono-data text-[11px] text-zinc-100 font-bold">{fmtM(r.hammer, r.currency)}</p>
                    </div>
                    <div className="col-span-1">
                      <span className={`font-mono-data text-[10px] font-bold ${isHigh ? 'text-green-400' : 'text-yellow-400'}`}>
                        +{pct}%
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </section>

        </div>
      </div>
    </div>
  )
}
