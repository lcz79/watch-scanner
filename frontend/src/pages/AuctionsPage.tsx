import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useLang } from '../lib/lang'
import {
  getAuctionRecords,
  getAuctionCalendar,
  getAuctionStats,
  getRecentAuctionResults,
  getAuctionRefreshStatus,
  triggerAuctionRefresh,
} from '../lib/api'
import type { AuctionResult, UpcomingAuction } from '../types'
import { fmtEur, fmtEurRange } from '../lib/currency'
import { isValidHttpUrl } from './SearchPage'

// ---------------------------------------------------------------------------
// Static house definitions
// ---------------------------------------------------------------------------

const HOUSES = [
  { id: 'christies',  name: "Christie's",  url: 'https://www.christies.com/en/departments/watches-52-1.aspx',  loc: 'Geneva · New York · Hong Kong', status: 'active' as const,  specialty: 'Important Watches — May & Nov' },
  { id: 'phillips',   name: 'Phillips',    url: 'https://www.phillipswatches.com',                             loc: 'Geneva · New York · Hong Kong', status: 'active' as const,  specialty: 'Watches — May & Nov + Online' },
  { id: 'sothebys',   name: "Sotheby's",   url: 'https://www.sothebys.com/en/departments/watches',             loc: 'Geneva · London · New York',    status: 'active' as const,  specialty: 'Important Watches — May & Nov' },
  { id: 'antiquorum', name: 'Antiquorum',  url: 'https://www.antiquorum.swiss/en/upcoming-auctions',           loc: 'Geneva · Hong Kong',            status: 'active' as const,  specialty: 'Modern & Vintage Timepieces' },
  { id: 'artcurial',  name: 'Artcurial',   url: 'https://www.artcurial.com/fr/departements/montres',           loc: 'Paris · Monaco',                status: 'active' as const,  specialty: 'Montres de Collection' },
  { id: 'cambi',      name: 'Cambi',       url: 'https://www.cambiaste.com',                                   loc: 'Genova · Italia',               status: 'active' as const,  specialty: 'Gioielli, Orologi & Preziosi' },
  { id: 'bolaffi',    name: 'Bolaffi',     url: 'https://www.astebolaffi.it',                                  loc: 'Torino · Italia',               status: 'active' as const,  specialty: 'Aste Gioielli e Orologi' },
  { id: 'bonhams',    name: 'Bonhams',     url: 'https://www.bonhams.com/departments/WAT-watches/',            loc: 'London · Los Angeles',          status: 'active' as const,  specialty: 'Watches & Clocks' },
]

// Colori per casa d'aste
const HOUSE_COLORS: Record<string, string> = {
  "Phillips":    "text-violet-400 bg-violet-400/10 border-violet-400/20",
  "Christie's":  "text-red-400 bg-red-400/10 border-red-400/20",
  "Sotheby's":   "text-blue-400 bg-blue-400/10 border-blue-400/20",
  "Antiquorum":  "text-amber-400 bg-amber-400/10 border-amber-400/20",
  "Artcurial":   "text-pink-400 bg-pink-400/10 border-pink-400/20",
  "Bonhams":     "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
  "Cambi":       "text-green-400 bg-green-400/10 border-green-400/20",
  "Bolaffi":     "text-cyan-400 bg-cyan-400/10 border-cyan-400/20",
}

const houseColor = (name: string) => HOUSE_COLORS[name] ?? "text-zinc-400 bg-zinc-400/10 border-zinc-400/20"
const houseTextColor = (name: string) => houseColor(name).split(' ')[0]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtPrice(n: number | null | undefined, _cur?: string) {
  return fmtEur(n)
}

function fmtDate(iso: string | null | undefined, lang: string) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', {
      day: 'numeric', month: 'long', year: 'numeric',
    })
  } catch { return iso }
}

function fmtShort(iso: string | null | undefined) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch { return iso }
}

function isPast(dateStr: string) {
  return new Date(dateStr) < new Date()
}

// ---------------------------------------------------------------------------
// Components
// ---------------------------------------------------------------------------

function AuctionCalendarCard({ auction, lang }: { auction: UpcomingAuction; lang: string }) {
  const past = isPast(auction.date)
  const href = auction.catalog_url || auction.url || '#'

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="block group border border-zinc-800 hover:border-primary/40 bg-zinc-900 hover:bg-zinc-800/50 transition-all"
    >
      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest border ${houseColor(auction.house)}`}>
            {auction.house}
          </span>
          <div className="flex items-center gap-1.5">
            {past ? (
              <span className="font-mono-data text-[9px] text-zinc-600 uppercase">Passata</span>
            ) : (
              <span className="flex items-center gap-1 font-mono-data text-[9px] text-green-400 uppercase">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                Upcoming
              </span>
            )}
            <span className="material-symbols-outlined text-[12px] text-zinc-600 group-hover:text-zinc-300 transition-colors">open_in_new</span>
          </div>
        </div>

        {/* Sale name */}
        <p className="font-['Space_Grotesk'] font-semibold text-sm text-zinc-100 leading-snug mb-2 group-hover:text-yellow-400 transition-colors">
          {auction.sale_name}
        </p>

        {/* Date + location */}
        <div className="flex items-center gap-3 text-[10px] text-zinc-500 mb-2">
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[12px]">calendar_today</span>
            {fmtShort(auction.date)}
          </span>
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[12px]">location_on</span>
            {auction.location}
          </span>
        </div>

        {/* Focus */}
        {auction.focus && (
          <p className="text-[10px] text-zinc-600 leading-relaxed line-clamp-2">{auction.focus}</p>
        )}

        {/* Catalog link pill */}
        {(auction.catalog_url || auction.url) && (
          <div className="mt-3 flex items-center gap-1 text-[9px] text-primary/70 group-hover:text-primary transition-colors font-mono-data uppercase tracking-widest">
            <span className="material-symbols-outlined text-[11px]">menu_book</span>
            {past ? 'Vedi Risultati' : 'Vedi Catalogo'}
          </div>
        )}
      </div>
    </a>
  )
}

function RecordRow({ record, index }: { record: AuctionResult; index: number }) {
  const hammer = record.hammer_price_chf
  const estimate = record.estimate_midpoint_chf || record.estimate_low_chf
  const ratio = hammer && estimate ? hammer / estimate : null
  const pct = ratio ? ((ratio - 1) * 100).toFixed(0) : null

  const href = isValidHttpUrl(record.lot_url)
    ? record.lot_url as string
    : `https://www.google.com/search?q=${encodeURIComponent(`${record.auction_house} ${record.brand} ${record.reference || record.model} ${record.sale_date?.slice(0, 4) || ''}`)}`

  return (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className="grid grid-cols-12 gap-2 px-4 py-3 border-b border-zinc-800 hover:bg-zinc-800/40 transition-colors items-center">
      <div className="col-span-1 font-mono-data text-[11px] text-zinc-600">{String(index + 1).padStart(2, '0')}</div>
      <div className="col-span-4">
        <p className="font-['Space_Grotesk'] text-xs font-semibold text-zinc-200 leading-tight truncate">
          {record.reference || record.model}
        </p>
        <p className="font-mono-data text-[9px] text-zinc-500">{record.brand}</p>
      </div>
      <div className="col-span-2">
        <span className={`px-1.5 py-0.5 text-[9px] font-bold uppercase border ${houseColor(record.auction_house)}`}>
          {record.auction_house.replace("Christie's", "Chr.").replace("Sotheby's", "Soth.")}
        </span>
      </div>
      <div className="col-span-1 font-mono-data text-[10px] text-zinc-500 text-center">
        {record.sale_date ? new Date(record.sale_date).getFullYear() : '—'}
      </div>
      <div className="col-span-2 font-mono-data text-[10px] text-zinc-500 text-right">
        {fmtPrice(record.estimate_low_chf)}
      </div>
      <div className="col-span-2 text-right">
        <p className="font-mono-data text-xs text-zinc-100 font-bold">{fmtPrice(hammer)}</p>
        {pct && (
          <p className={`font-mono-data text-[9px] ${Number(pct) > 0 ? 'text-green-400' : 'text-red-400'}`}>
            +{pct}%
          </p>
        )}
      </div>
    </a>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function AuctionsPage() {
  const { t, lang } = useLang()
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<'upcoming' | 'past'>('upcoming')
  const [houseFilter, setHouseFilter] = useState<string>('all')
  const [refreshToast, setRefreshToast] = useState<string | null>(null)

  // ── Data fetching ──────────────────────────────────────────────────────────
  const { data: stats } = useQuery({
    queryKey: ['auction-stats'],
    queryFn: getAuctionStats,
    staleTime: 5 * 60 * 1000,
  })

  const { data: upcomingData = [], isLoading: upcomingLoading } = useQuery({
    queryKey: ['auction-calendar-upcoming'],
    queryFn: () => getAuctionCalendar({ include_past: false }),
    staleTime: 10 * 60 * 1000,
  })

  const { data: pastData = [], isLoading: pastLoading } = useQuery({
    queryKey: ['auction-calendar-past'],
    queryFn: () => getAuctionCalendar({ include_past: true }),
    staleTime: 10 * 60 * 1000,
    select: data => data.filter((a: UpcomingAuction) => isPast(a.date))
                        .sort((a: UpcomingAuction, b: UpcomingAuction) =>
                          new Date(b.date).getTime() - new Date(a.date).getTime()
                        ),
  })

  const { data: recordsData = [], isLoading: recordsLoading } = useQuery({
    queryKey: ['auction-records'],
    queryFn: () => getAuctionRecords({ limit: 30 }),
    staleTime: 5 * 60 * 1000,
  })

  const { data: recentData } = useQuery({
    queryKey: ['auction-recent'],
    queryFn: () => getRecentAuctionResults(6),
    staleTime: 5 * 60 * 1000,
  })

  const { data: refreshStatus } = useQuery({
    queryKey: ['auction-refresh-status'],
    queryFn: getAuctionRefreshStatus,
    refetchInterval: (query) => (query.state.data as { is_running?: boolean } | undefined)?.is_running ? 5_000 : 30_000,
    staleTime: 0,
  })

  const refreshMutation = useMutation({
    mutationFn: triggerAuctionRefresh,
    onSuccess: (data) => {
      setRefreshToast(data.message)
      setTimeout(() => setRefreshToast(null), 6000)
      queryClient.invalidateQueries({ queryKey: ['auction-refresh-status'] })
    },
  })

  // ── Derived ────────────────────────────────────────────────────────────────
  const calendarData = tab === 'upcoming'
    ? upcomingData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    : pastData

  const normalise = (s: string) => s.toLowerCase().replace(/['']/g, "'").replace(/\s+/g, ' ').trim()
  const filteredCalendar = houseFilter === 'all'
    ? calendarData
    : calendarData.filter(a => normalise(a.house) === normalise(houseFilter))

  const records = [...recordsData]
    .filter(r => r.hammer_price_chf && r.hammer_price_chf > 0)
    .sort((a, b) => (b.hammer_price_chf ?? 0) - (a.hammer_price_chf ?? 0))

  const totalLots = stats?.total_lots_in_db ?? 0
  const isRefreshing = refreshStatus?.is_running ?? false

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="p-6 lg:p-8 max-w-[1600px] mx-auto space-y-8">

      {/* Toast */}
      {refreshToast && (
        <div className="fixed bottom-6 right-6 z-50 bg-zinc-800 border border-primary/40 px-5 py-3 rounded shadow-xl max-w-sm">
          <p className="text-sm text-zinc-200">{refreshToast}</p>
        </div>
      )}

      {/* ── Header ── */}
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <span className="font-label-caps text-primary text-[10px] uppercase tracking-[0.2em] mb-2 block">
            {t.surveillanceLabel}
          </span>
          <h1 className="font-h1 text-on-surface text-3xl">{t.auctionIntelligence}</h1>
          <p className="text-zinc-500 text-sm mt-1">{t.auctionIntelligenceSub}</p>
        </div>
        <div className="flex items-center gap-6 flex-wrap">
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">Case d'aste</p>
            <p className="font-display-price text-2xl text-primary">{HOUSES.length}</p>
          </div>
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">Lots in DB</p>
            <p className="font-display-price text-2xl text-primary">
              {totalLots > 0 ? totalLots.toLocaleString() : '—'}
            </p>
          </div>
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">Aste in calendario</p>
            <p className="font-display-price text-2xl text-primary">
              {(upcomingData.length + pastData.length) || '—'}
            </p>
          </div>
          <button
            onClick={() => refreshMutation.mutate()}
            disabled={isRefreshing || refreshMutation.isPending}
            className={`flex items-center gap-2 px-4 py-2.5 text-[10px] font-bold uppercase tracking-widest border transition-colors rounded ${
              isRefreshing || refreshMutation.isPending
                ? 'border-yellow-400/20 text-yellow-400/40 cursor-not-allowed'
                : 'border-primary/40 text-primary hover:bg-primary/10'
            }`}
          >
            <span className={`material-symbols-outlined text-[14px] ${isRefreshing ? 'animate-spin' : ''}`}>sync</span>
            {isRefreshing ? 'Scraping...' : 'Refresh Data'}
          </button>
        </div>
      </div>

      {/* Refresh status bar */}
      {refreshStatus?.last_run && (
        <div className="flex items-center gap-3 text-[10px] text-zinc-500 font-mono-data bg-zinc-900/50 border border-zinc-800 px-4 py-2 rounded">
          <span className={`w-1.5 h-1.5 rounded-full ${isRefreshing ? 'bg-yellow-400 animate-pulse' : refreshStatus.last_run_status === 'success' ? 'bg-green-500' : 'bg-red-500'}`} />
          <span>
            {isRefreshing ? 'Scraping in corso...' : `Ultimo refresh: ${fmtDate(refreshStatus.last_run, lang)} · ${refreshStatus.last_run_status}`}
          </span>
          {totalLots > 0 && <span className="ml-auto text-zinc-600">{totalLots.toLocaleString()} lotti in DB</span>}
        </div>
      )}

      {/* ── Main grid ── */}
      <div className="grid grid-cols-12 gap-8">

        {/* ── LEFT: Calendar ── */}
        <div className="col-span-12 xl:col-span-7 space-y-5">

          {/* Tab switcher */}
          <div className="flex items-center justify-between">
            <div className="flex gap-0 border border-zinc-800">
              {(['upcoming', 'past'] as const).map(t => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`px-4 py-2 text-[10px] font-bold uppercase tracking-widest transition-colors ${
                    tab === t
                      ? 'bg-primary text-zinc-950'
                      : 'text-zinc-500 hover:text-zinc-200'
                  }`}
                >
                  {t === 'upcoming' ? `Prossime (${upcomingData.length})` : `Passate (${pastData.length})`}
                </button>
              ))}
            </div>

            {/* House filter chips */}
            <div className="flex gap-1 flex-wrap justify-end">
              <button
                onClick={() => setHouseFilter('all')}
                className={`px-2.5 py-1 text-[9px] font-bold uppercase tracking-widest rounded transition-colors ${
                  houseFilter === 'all' ? 'bg-primary text-zinc-950' : 'bg-zinc-900 text-zinc-500 border border-zinc-800 hover:text-zinc-200'
                }`}
              >All</button>
              {HOUSES.map(h => (
                <button
                  key={h.id}
                  onClick={() => setHouseFilter(houseFilter === h.name ? 'all' : h.name)}
                  className={`px-2.5 py-1 text-[9px] font-bold uppercase tracking-widest rounded transition-colors border ${
                    houseFilter === h.name
                      ? houseColor(h.name)
                      : 'bg-zinc-900 text-zinc-600 border-zinc-800 hover:text-zinc-200'
                  }`}
                >
                  {h.name.replace("Christie's", "Chr.").replace("Sotheby's", "Soth.")}
                </button>
              ))}
            </div>
          </div>

          {/* Calendar grid */}
          {(upcomingLoading || pastLoading) ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 p-4 animate-pulse h-32" />
              ))}
            </div>
          ) : filteredCalendar.length === 0 ? (
            <div className="border border-zinc-800 p-10 text-center bg-zinc-900">
              <span className="material-symbols-outlined text-4xl text-zinc-700 block mb-3">calendar_month</span>
              <p className="text-zinc-500 text-sm">
                {houseFilter !== 'all'
                  ? `Nessuna asta ${houseFilter} in questa vista.`
                  : tab === 'upcoming' ? 'Nessuna asta futura in calendario.' : 'Nessuna asta passata.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredCalendar.map((a, i) => (
                <AuctionCalendarCard key={i} auction={a} lang={lang} />
              ))}
            </div>
          )}
        </div>

        {/* ── RIGHT: Houses + Records ── */}
        <div className="col-span-12 xl:col-span-5 space-y-6">

          {/* Connected houses */}
          <section className="bg-zinc-900 border border-zinc-800">
            <div className="px-5 py-3 border-b border-zinc-800">
              <h3 className="font-h2 text-xs uppercase tracking-tight">{t.connectedSources}</h3>
            </div>
            <div className="divide-y divide-zinc-800">
              {HOUSES.map(h => {
                const breakdown = stats?.houses_breakdown?.find(hb => hb.house === h.name)
                return (
                  <a key={h.id} href={h.url} target="_blank" rel="noopener noreferrer"
                    className="px-4 py-3 flex items-center justify-between gap-3 hover:bg-zinc-800/50 transition-colors">
                    <div className="min-w-0 flex items-center gap-2">
                      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${h.status === 'active' ? 'bg-green-500' : 'bg-zinc-600'}`} />
                      <div>
                        <p className={`text-sm font-['Space_Grotesk'] font-medium ${houseTextColor(h.name)}`}>{h.name}</p>
                        <p className="text-[9px] text-zinc-600">{h.loc}</p>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0 flex items-center gap-3">
                      {breakdown && breakdown.lots > 0 && (
                        <span className="font-mono-data text-[9px] text-zinc-600">{breakdown.lots} lots</span>
                      )}
                      <span className="material-symbols-outlined text-[12px] text-zinc-600">open_in_new</span>
                    </div>
                  </a>
                )
              })}
            </div>
          </section>

          {/* Top records */}
          <section className="bg-zinc-900 border border-zinc-800">
            <div className="px-5 py-3 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="font-h2 text-xs uppercase tracking-tight">{t.recordPricesLabel}</h3>
              <span className="font-mono-data text-[9px] text-zinc-600">{records.length} risultati in DB</span>
            </div>

            {recordsLoading ? (
              <div className="p-6 animate-pulse space-y-3">
                {[...Array(5)].map((_, i) => <div key={i} className="h-4 bg-zinc-800 rounded" />)}
              </div>
            ) : records.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-zinc-600 text-xs">Nessun record in DB. Premi Refresh Data.</p>
              </div>
            ) : (
              <>
                {/* Header */}
                <div className="grid grid-cols-12 gap-2 px-4 py-2 border-b border-zinc-800 bg-zinc-950">
                  {['#', 'Referenza', 'Casa', 'Anno', 'Stima', 'Hammer'].map((h, i) => (
                    <div key={i} className={`font-label-caps text-[9px] text-zinc-600 uppercase ${
                      i === 0 ? 'col-span-1' : i === 1 ? 'col-span-4' : i === 2 ? 'col-span-2' : i === 3 ? 'col-span-1' : 'col-span-2'
                    }`}>{h}</div>
                  ))}
                </div>
                {records.slice(0, 12).map((r, i) => (
                  <RecordRow key={r.id ?? i} record={r} index={i} />
                ))}
              </>
            )}
          </section>

          {/* Recent lots */}
          {recentData && recentData.results.length > 0 && (
            <section className="bg-zinc-900 border border-zinc-800">
              <div className="px-5 py-3 border-b border-zinc-800 flex items-center justify-between">
                <h3 className="font-h2 text-xs uppercase tracking-tight">Ultimi Risultati in DB</h3>
                <span className="font-mono-data text-[9px] text-zinc-500">
                  {new Date().toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()} · {new Date().toLocaleTimeString(lang === 'it' ? 'it-IT' : 'en-GB', { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="divide-y divide-zinc-800">
                {recentData.results.slice(0, 5).map((lot, i) => {
                  const href = isValidHttpUrl(lot.lot_url) ? lot.lot_url as string : `https://www.google.com/search?q=${encodeURIComponent(`${lot.auction_house} ${lot.brand} ${lot.reference || lot.model}`)}`
                  return (
                    <a key={lot.id ?? i} href={href} target="_blank" rel="noopener noreferrer"
                      className="px-4 py-3 flex items-center justify-between gap-3 hover:bg-zinc-800/40 transition-colors group">
                      <div className="min-w-0">
                        <p className="text-xs text-zinc-200 font-['Space_Grotesk'] font-medium truncate group-hover:text-yellow-400 transition-colors">
                          {lot.reference || lot.model}
                        </p>
                        <p className="text-[9px] text-zinc-600">{lot.brand} · {fmtShort(lot.sale_date)}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="font-mono-data text-xs text-zinc-100 font-bold">{fmtPrice(lot.hammer_price_chf)}</p>
                        <span className={`text-[9px] font-bold uppercase ${houseTextColor(lot.auction_house)}`}>{lot.auction_house}</span>
                      </div>
                    </a>
                  )
                })}
              </div>
            </section>
          )}

        </div>
      </div>
    </div>
  )
}
