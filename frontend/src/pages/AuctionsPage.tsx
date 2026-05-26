import { useState, useEffect } from 'react'
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

// ---------------------------------------------------------------------------
// Static fallback data (used when DB is empty or API unavailable)
// ---------------------------------------------------------------------------

const HOUSES = [
  { id: 'christies',  name: "Christie's",  url: 'https://www.christies.com/departments/watches',   loc: 'Geneva · New York · Hong Kong', status: 'active' as const,   specialty: 'Important Watches — May & Nov' },
  { id: 'phillips',   name: 'Phillips',    url: 'https://www.phillips.com/watches',                loc: 'Geneva · New York · Hong Kong', status: 'active' as const,   specialty: 'Watches — May & Nov + Online' },
  { id: 'sothebys',   name: "Sotheby's",   url: 'https://www.sothebys.com/en/departments/watches', loc: 'Geneva · London · New York',    status: 'active' as const,   specialty: 'Important Watches — May & Nov' },
  { id: 'antiquorum', name: 'Antiquorum',  url: 'https://www.antiquorum.swiss',                    loc: 'Geneva · Hong Kong',            status: 'active' as const,   specialty: 'Modern & Vintage Timepieces' },
  { id: 'artcurial',  name: 'Artcurial',   url: 'https://www.artcurial.com/fr/departements/montres', loc: 'Paris · Monaco',             status: 'active' as const,   specialty: 'Montres de Collection' },
  { id: 'bonhams',    name: 'Bonhams',     url: 'https://www.bonhams.com/departments/WAT/',        loc: 'London · Los Angeles',          status: 'pending' as const,  specialty: 'Watches & Clocks' },
  { id: 'dorotheum',  name: 'Dorotheum',   url: 'https://www.dorotheum.com/en/auctions/watch-auctions/', loc: 'Vienna · Prague',       status: 'pending' as const,  specialty: 'Uhren & Taschenuhren' },
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtM(n: number, cur = '') {
  const suffix = cur ? ` ${cur}` : ''
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M${suffix}`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K${suffix}`
  return `${n.toLocaleString()}${suffix}`
}

function fmtPrice(n: number | null | undefined, cur = 'CHF') {
  if (!n) return '—'
  return fmtM(n, cur)
}

function fmtDate(iso: string, lang: string) {
  try {
    return new Date(iso).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch { return iso }
}

function fmtShortDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
  } catch { return iso }
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
        { val: d, label: d === 1 ? t.dayLabel : t.daysLabel },
        { val: h, label: t.hoursLabel },
        { val: m, label: t.minutesLabel },
        { val: s, label: 's' },
      ].map(({ val, label }) => (
        <div key={label} className="text-center">
          <p className="font-display-price text-2xl text-primary leading-none">{String(val).padStart(2, '0')}</p>
          <p className="font-mono-data text-[9px] text-zinc-500 uppercase mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  )
}

function AuctionRecordRow({ record, index, sortField }: {
  record: AuctionResult
  index: number
  sortField: 'hammer' | 'estimate'
}) {
  const hammer = record.hammer_price_chf
  const estimate = record.estimate_midpoint_chf || record.estimate_low_chf
  const ratio = hammer && estimate ? hammer / estimate : null
  const pct = ratio ? ((ratio - 1) * 100).toFixed(0) : null
  const isHigh = ratio ? ratio > 2 : false

  const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(`${record.auction_house} ${record.brand} ${record.reference || record.model} auction result ${record.sale_date?.slice(0, 4) || ''}`)}`
  const href = record.lot_url || searchUrl

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="grid grid-cols-12 gap-3 px-4 py-3 border-b border-zinc-800 hover:bg-zinc-800/40 transition-colors items-center cursor-pointer"
    >
      <div className="col-span-1 font-mono-data text-[11px] text-zinc-600">{String(index + 1).padStart(2, '0')}</div>
      <div className="col-span-3">
        <p className="text-xs text-zinc-200 font-['Space_Grotesk'] font-medium leading-tight">
          {record.reference || record.model}
        </p>
        <p className="font-mono-data text-[9px] text-zinc-500">{record.brand}</p>
      </div>
      <div className="col-span-2">
        <p className="font-mono-data text-[10px] text-zinc-400">{record.auction_house}</p>
      </div>
      <div className="col-span-1">
        <p className="font-mono-data text-[10px] text-zinc-500">
          {record.sale_date ? new Date(record.sale_date).getFullYear() : '—'}
        </p>
      </div>
      <div className="col-span-2">
        <p className="font-mono-data text-[11px] text-zinc-500">
          {sortField === 'estimate'
            ? fmtPrice(estimate)
            : fmtPrice(record.estimate_low_chf)
          }
        </p>
      </div>
      <div className="col-span-2">
        <p className="font-mono-data text-[11px] text-zinc-100 font-bold">{fmtPrice(hammer)}</p>
      </div>
      <div className="col-span-1">
        {pct ? (
          <span className={`font-mono-data text-[10px] font-bold ${isHigh ? 'text-green-400' : 'text-yellow-400'}`}>
            +{pct}%
          </span>
        ) : (
          <span className="font-mono-data text-[10px] text-zinc-600">—</span>
        )}
      </div>
    </a>
  )
}

function UpcomingAuctionRow({ auction, lang }: { auction: UpcomingAuction; lang: string }) {
  const href = auction.catalog_url || auction.url || `https://www.google.com/search?q=${encodeURIComponent(`${auction.house} ${auction.sale_name} watch auction`)}`
  const isPast = new Date(auction.date) < new Date()

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="px-5 py-4 hover:bg-zinc-800/40 transition-colors group block border-b border-zinc-800 last:border-b-0"
    >
      <div className="flex items-start justify-between mb-1">
        <span className="font-label-caps text-[9px] text-primary uppercase tracking-widest">{auction.house}</span>
        {isPast && (
          <span className="font-mono-data text-[8px] text-zinc-600 uppercase">Past</span>
        )}
        {auction.catalog_url && (
          <span className="font-mono-data text-[8px] text-green-400/80 uppercase flex items-center gap-0.5">
            <span className="material-symbols-outlined text-[10px]">link</span>
            Catalog
          </span>
        )}
      </div>
      <p className="text-sm text-zinc-200 leading-snug mb-2 group-hover:text-yellow-400 transition-colors">
        {auction.sale_name}
      </p>
      <div className="flex items-center justify-between text-[10px] text-zinc-500">
        <span className="flex items-center gap-1">
          <span className="material-symbols-outlined text-[12px]">calendar_today</span>
          {fmtDate(auction.date, lang)} · {auction.location || '—'}
        </span>
        {auction.focus && (
          <span className="text-zinc-600 truncate max-w-[120px]">{auction.focus}</span>
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
  const [houseFilter, setHouseFilter] = useState<string>('all')
  const [sortField, setSortField] = useState<'hammer' | 'estimate'>('hammer')
  const [refreshToast, setRefreshToast] = useState<string | null>(null)

  // ── Data fetching ──────────────────────────────────────────────────────────
  const { data: stats } = useQuery({
    queryKey: ['auction-stats'],
    queryFn: getAuctionStats,
    staleTime: 5 * 60 * 1000,
  })

  const { data: recordsData, isLoading: recordsLoading } = useQuery({
    queryKey: ['auction-records', sortField],
    queryFn: () => getAuctionRecords({ limit: 20 }),
    staleTime: 5 * 60 * 1000,
  })

  const { data: calendarData, isLoading: calendarLoading } = useQuery({
    queryKey: ['auction-calendar'],
    queryFn: getAuctionCalendar,
    staleTime: 10 * 60 * 1000,
  })

  const { data: recentData } = useQuery({
    queryKey: ['auction-recent'],
    queryFn: () => getRecentAuctionResults(12),
    staleTime: 5 * 60 * 1000,
  })

  const { data: refreshStatus } = useQuery({
    queryKey: ['auction-refresh-status'],
    queryFn: getAuctionRefreshStatus,
    refetchInterval: 10_000, // poll every 10s while running
    staleTime: 0,
  })

  const refreshMutation = useMutation({
    mutationFn: triggerAuctionRefresh,
    onSuccess: (data) => {
      setRefreshToast(data.message)
      setTimeout(() => setRefreshToast(null), 5000)
      queryClient.invalidateQueries({ queryKey: ['auction-refresh-status'] })
    },
  })

  // ── Derived data ───────────────────────────────────────────────────────────
  const records = (recordsData ?? []).filter(r => sortField === 'hammer'
    ? (r.hammer_price_chf ?? 0) > 0
    : (r.estimate_low_chf ?? 0) > 0
  ).sort((a, b) => sortField === 'hammer'
    ? (b.hammer_price_chf ?? 0) - (a.hammer_price_chf ?? 0)
    : (b.estimate_low_chf ?? 0) - (a.estimate_low_chf ?? 0)
  )

  const calendar = (calendarData ?? []).sort((a, b) =>
    new Date(a.date).getTime() - new Date(b.date).getTime()
  )

  const upcomingAuctions = calendar.filter(a => new Date(a.date) >= new Date())
  const nextAuction = upcomingAuctions[0]

  const recent = recentData?.results ?? []
  const filteredRecent = houseFilter === 'all'
    ? recent
    : recent.filter(r => r.auction_house.toLowerCase().includes(houseFilter))

  const totalLots = stats?.total_lots_in_db ?? 0
  const isRefreshing = refreshStatus?.is_running ?? false

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-10">

      {/* Toast */}
      {refreshToast && (
        <div className="fixed bottom-6 right-6 z-50 bg-zinc-800 border border-zinc-700 px-5 py-3 rounded shadow-lg max-w-sm">
          <p className="text-sm text-zinc-200">{refreshToast}</p>
        </div>
      )}

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <span className="font-label-caps text-primary text-[10px] uppercase tracking-[0.2em] mb-2 block">
            {t.surveillanceLabel}
          </span>
          <h1 className="font-h1 text-on-surface text-3xl">{t.auctionIntelligence}</h1>
          <p className="text-zinc-500 text-sm mt-1 max-w-xl">{t.auctionIntelligenceSub}</p>
        </div>
        <div className="flex items-center gap-8 flex-wrap">
          {/* KPIs */}
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">{t.housesConnected}</p>
            <p className="font-display-price text-2xl text-primary">
              {HOUSES.filter(h => h.status === 'active').length}
              <span className="text-zinc-600 text-sm">/{HOUSES.length}</span>
            </p>
          </div>
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">Lots in DB</p>
            <p className="font-display-price text-2xl text-primary">
              {totalLots > 0 ? totalLots.toLocaleString() : '—'}
            </p>
          </div>
          {/* Countdown to next auction */}
          {nextAuction ? (
            <div className="bg-zinc-900 border border-zinc-800 px-5 py-3 rounded">
              <p className="font-mono-data text-[9px] text-zinc-500 uppercase mb-2">{t.nextAuction}</p>
              <CountdownBlock targetISO={nextAuction.date} />
            </div>
          ) : null}
          {/* Refresh button */}
          <button
            onClick={() => refreshMutation.mutate()}
            disabled={isRefreshing || refreshMutation.isPending}
            className={`flex items-center gap-2 px-4 py-2.5 text-[10px] font-bold uppercase tracking-widest border transition-colors rounded ${
              isRefreshing || refreshMutation.isPending
                ? 'border-yellow-400/30 text-yellow-400/50 cursor-not-allowed'
                : 'border-primary/40 text-primary hover:bg-primary/10'
            }`}
          >
            <span className={`material-symbols-outlined text-[14px] ${isRefreshing ? 'animate-spin' : ''}`}>
              sync
            </span>
            {isRefreshing ? 'Scanning...' : 'Refresh Data'}
          </button>
        </div>
      </div>

      {/* Refresh status bar */}
      {refreshStatus && (refreshStatus.last_run || refreshStatus.is_running) && (
        <div className="flex items-center gap-3 text-[10px] text-zinc-500 font-mono-data bg-zinc-900/50 border border-zinc-800 px-4 py-2 rounded">
          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
            refreshStatus.is_running ? 'bg-yellow-400 animate-pulse' :
            refreshStatus.last_run_status === 'success' ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span>
            {refreshStatus.is_running
              ? 'Scraping in corso...'
              : `Ultimo refresh: ${refreshStatus.last_run ? fmtDate(refreshStatus.last_run, lang) : '—'} · Status: ${refreshStatus.last_run_status}`
            }
          </span>
          {refreshStatus.next_run && !refreshStatus.is_running && (
            <span className="ml-auto text-zinc-600">
              Prossimo: {fmtDate(refreshStatus.next_run, lang)}
            </span>
          )}
          {refreshStatus.total_in_db !== undefined && (
            <span className="ml-auto text-zinc-600">
              {refreshStatus.total_in_db.toLocaleString()} lotti in DB
            </span>
          )}
        </div>
      )}

      {/* ── Main grid ──────────────────────────────────────────── */}
      <div className="grid grid-cols-12 gap-8">

        {/* ── Left column ──────────────────────────── */}
        <div className="col-span-12 lg:col-span-4 space-y-6">

          {/* Upcoming calendar */}
          <section className="bg-zinc-900 border border-zinc-800">
            <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="font-h2 text-sm uppercase tracking-tight">{t.auctionCalendarTitle}</h3>
              <span className="font-mono-data text-[10px] text-zinc-500">
                {calendarLoading ? '…' : `${calendar.length} sales`}
              </span>
            </div>
            <div className="max-h-[480px] overflow-y-auto">
              {calendarLoading ? (
                <div className="px-5 py-8 text-center text-zinc-600 text-sm">Loading calendar…</div>
              ) : calendar.length === 0 ? (
                <div className="px-5 py-8 text-center text-zinc-600 text-sm">No auction data</div>
              ) : (
                calendar.slice(0, 12).map((a, i) => (
                  <UpcomingAuctionRow key={i} auction={a} lang={lang} />
                ))
              )}
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

            {/* Scraping info */}
            <div className="px-5 py-3 border-b border-zinc-800 bg-zinc-950/50 space-y-1.5">
              {[
                { icon: 'database',      label: `${totalLots} lotti nel database` },
                { icon: 'calendar_month', label: t.scrapingCalendar },
                { icon: 'task_alt',       label: t.scrapingResults },
              ].map(({ icon, label }) => (
                <div key={label} className="flex items-center gap-2 text-[10px] text-zinc-500">
                  <span className="material-symbols-outlined text-[12px] text-yellow-400">{icon}</span>
                  <span className="font-mono-data">{label}</span>
                </div>
              ))}
            </div>

            <div className="divide-y divide-zinc-800">
              {HOUSES.map(h => {
                const breakdown = stats?.houses_breakdown?.find(hb => hb.house === h.name)
                return (
                  <a key={h.id} href={h.url} target="_blank" rel="noopener noreferrer"
                    className="px-5 py-3 flex items-center justify-between gap-3 hover:bg-zinc-800/50 transition-colors cursor-pointer">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${h.status === 'active' ? 'bg-green-500' : 'bg-zinc-600'}`} />
                        <p className="font-['Space_Grotesk'] text-sm text-zinc-200 truncate hover:text-yellow-400 transition-colors">{h.name}</p>
                        <span className="material-symbols-outlined text-[11px] text-zinc-600">open_in_new</span>
                      </div>
                      <p className="text-[10px] text-zinc-500 truncate pl-3.5">{h.loc}</p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className={`font-label-caps text-[9px] uppercase ${h.status === 'active' ? 'text-green-400' : 'text-zinc-600'}`}>
                        {h.status === 'active' ? t.sourceActive : t.sourcePending}
                      </p>
                      {breakdown && breakdown.lots > 0 && (
                        <p className="font-mono-data text-[9px] text-zinc-600">{breakdown.lots} lots</p>
                      )}
                    </div>
                  </a>
                )
              })}
            </div>

            <div className="px-5 py-3 border-t border-zinc-800 bg-zinc-950/30">
              <p className="text-[10px] text-zinc-600 leading-relaxed">
                {lang === 'it'
                  ? 'Dati via scraping HTML · Refresh automatico settimanale'
                  : 'Data via HTML scraping · Weekly auto-refresh'}
              </p>
            </div>
          </section>
        </div>

        {/* ── Right column ─────────────────────────── */}
        <div className="col-span-12 lg:col-span-8 space-y-8">

          {/* Recent results */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-h2 text-sm uppercase tracking-tight">
                {lang === 'it' ? 'Risultati Recenti' : 'Recent Results'}
                {recentData && (
                  <span className="ml-2 font-mono-data text-[10px] text-zinc-600 normal-case">
                    ({recentData.total_in_db.toLocaleString()} in DB)
                  </span>
                )}
              </h3>
              {/* House filter */}
              <div className="flex gap-1 flex-wrap">
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

            {filteredRecent.length === 0 ? (
              <div className="bg-zinc-900 border border-zinc-800 p-8 text-center">
                <span className="material-symbols-outlined text-4xl text-zinc-700 block mb-3">gavel</span>
                <p className="text-zinc-500 text-sm mb-2">
                  {lang === 'it' ? 'Nessun risultato in DB per questa casa d\'aste.' : 'No results in DB for this house.'}
                </p>
                <p className="text-zinc-600 text-xs">
                  {lang === 'it'
                    ? 'Usa il pulsante "Refresh Data" per avviare lo scraping.'
                    : 'Use the "Refresh Data" button to trigger scraping.'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {filteredRecent.slice(0, 9).map((lot, i) => {
                  const href = lot.lot_url || `https://www.google.com/search?q=${encodeURIComponent(`${lot.auction_house} ${lot.brand} ${lot.reference || lot.model}`)}`
                  return (
                    <a key={lot.id ?? i} href={href} target="_blank" rel="noopener noreferrer" className="block group">
                      <article className="bg-zinc-900 border border-zinc-800 hover:border-primary/40 transition-colors h-full">
                        {/* Image */}
                        <div className="h-36 bg-zinc-950 border-b border-zinc-800 flex items-center justify-center relative overflow-hidden">
                          {lot.image_url ? (
                            <img
                              src={lot.image_url}
                              alt={lot.description || lot.model}
                              className="h-full w-full object-cover opacity-70 group-hover:opacity-90 transition-opacity"
                              onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
                            />
                          ) : (
                            <span className="material-symbols-outlined text-5xl text-zinc-800 group-hover:text-zinc-700 transition-colors">watch</span>
                          )}
                          <div className="absolute top-2 left-2 bg-zinc-950/90 px-2 py-0.5">
                            <span className="font-mono-data text-[9px] text-primary uppercase">{lot.auction_house}</span>
                          </div>
                          {lot.lot_number && (
                            <div className="absolute top-2 right-2 bg-zinc-950/90 px-2 py-0.5">
                              <span className="font-mono-data text-[9px] text-zinc-400">{t.lotLabel} {lot.lot_number}</span>
                            </div>
                          )}
                        </div>

                        <div className="p-4">
                          <p className="font-label-caps text-[9px] text-zinc-500 uppercase mb-1">{lot.brand}</p>
                          <p className="font-['Space_Grotesk'] font-bold text-sm text-zinc-100 mb-1 leading-snug group-hover:text-yellow-400 transition-colors">
                            {lot.reference || lot.model}
                          </p>
                          {lot.description && lot.description !== lot.reference && (
                            <p className="text-[11px] text-zinc-500 mb-2 leading-relaxed line-clamp-2">
                              {lot.description}
                            </p>
                          )}

                          <div className="flex items-center justify-between text-[10px] text-zinc-500 mb-3">
                            <span className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[11px]">calendar_today</span>
                              {fmtShortDate(lot.sale_date)}
                              {lot.sale_name && ` · ${lot.sale_name.slice(0, 20)}${lot.sale_name.length > 20 ? '…' : ''}`}
                            </span>
                          </div>

                          <div className="flex items-center justify-between">
                            <div>
                              {lot.estimate_low_chf ? (
                                <>
                                  <p className="font-mono-data text-[9px] text-zinc-600 uppercase">{t.estimateLabel}</p>
                                  <p className="font-mono-data text-xs text-zinc-400">
                                    {fmtPrice(lot.estimate_low_chf)}–{fmtPrice(lot.estimate_high_chf)}
                                  </p>
                                </>
                              ) : null}
                            </div>
                            <div className="text-right">
                              <p className="font-mono-data text-[9px] text-zinc-600 uppercase">{t.hammerPriceLabel}</p>
                              <p className="font-mono-data text-sm text-zinc-100 font-bold">
                                {fmtPrice(lot.hammer_price_chf)}
                              </p>
                            </div>
                          </div>
                        </div>
                      </article>
                    </a>
                  )
                })}
              </div>
            )}
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

            {recordsLoading ? (
              <div className="bg-zinc-900 border border-zinc-800 p-8 text-center text-zinc-600 text-sm">
                Loading records…
              </div>
            ) : records.length === 0 ? (
              <div className="bg-zinc-900 border border-zinc-800 p-8 text-center">
                <p className="text-zinc-500 text-sm">No records in DB yet.</p>
                <p className="text-zinc-600 text-xs mt-1">Run a refresh to populate auction data.</p>
              </div>
            ) : (
              <div className="bg-zinc-900 border border-zinc-800 overflow-hidden">
                {/* Table header */}
                <div className="grid grid-cols-12 gap-3 px-4 py-2 border-b border-zinc-800 bg-zinc-950">
                  {(['#', 'Reference', t.saleLabel, 'Year', t.estimateLabel, t.hammerPriceLabel, 'vs Est.']).map((h, i) => (
                    <div key={i} className={`font-label-caps text-[9px] text-zinc-600 uppercase ${
                      i === 0 ? 'col-span-1' : i === 1 ? 'col-span-3' : i === 2 ? 'col-span-2' : i === 3 ? 'col-span-1' : 'col-span-2'
                    }`}>{h}</div>
                  ))}
                </div>

                {records.slice(0, 15).map((r, i) => (
                  <AuctionRecordRow key={r.id ?? i} record={r} index={i} sortField={sortField} />
                ))}
              </div>
            )}
          </section>

        </div>
      </div>
    </div>
  )
}
