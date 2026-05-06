import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { scanWatch, getPriceHistory, identifyWatchFromImage } from '../lib/api'
import type { WatchListing, ScanResult, MarketStats, InvestmentScore } from '../types'
import MarketCard from '../components/MarketCard'
import PriceEvolutionChart from '../components/PriceEvolutionChart'
import { clsx } from 'clsx'
import { formatDistanceToNow } from 'date-fns'
import { it as itLocale } from 'date-fns/locale'
import { useLang } from '../lib/lang'

const QUICK_REFS = ['116610LN', '126710BLNR', '5711/1A', '116500LN', '15500ST']

const ALL_SOURCES = ['chrono24', 'ebay', 'instagram', 'instagram_story', 'watchbox', 'watchfinder', 'subito', 'vision_ai', 'tiktok', 'reseller_website']

const SOURCE_LABELS: Record<string, string> = {
  chrono24: 'Chrono24',
  watchbox: 'WatchBox',
  ebay: 'eBay',
  watchfinder: 'Watchfinder',
  bobs_watches: "Bob's Watches",
  instagram: 'Instagram',
  instagram_story: 'Instagram Story',
  tiktok: 'TikTok',
  vision_ai: 'Vision AI',
  subito: 'Subito.it',
  reseller_website: 'Sito Reseller',
}

const SOURCE_COLORS: Record<string, string> = {
  chrono24: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
  watchbox: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
  ebay: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  watchfinder: 'text-green-400 bg-green-400/10 border-green-400/20',
  instagram: 'text-pink-400 bg-pink-400/10 border-pink-400/20',
  instagram_story: 'text-rose-400 bg-rose-400/10 border-rose-400/20',
  tiktok: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
  vision_ai: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
  subito: 'text-orange-400 bg-orange-400/10 border-orange-400/20',
  reseller_website: 'text-violet-400 bg-violet-400/10 border-violet-400/20',
}

const SCAN_STEPS = [
  { label: 'Connessione agli agenti', icon: 'wifi' },
  { label: 'Scansione Chrono24',       icon: 'language' },
  { label: 'Scansione eBay',           icon: 'sell' },
  { label: 'Analisi Instagram + Subito.it', icon: 'bolt' },
  { label: 'Aggregazione risultati',   icon: 'bar_chart' },
]

const SCAN_DURATIONS = [3000, 15000, 8000, 10000, 4000]

const EU_COUNTRIES = new Set(['IT','DE','FR','ES','NL','BE','AT','CH','PT','PL',
  'SE','NO','DK','FI','CZ','HU','RO','GR','SK','HR','SI','LU','IE','BG','LV',
  'LT','EE','MT','CY','GB','UK'])
const ITALY_KEYWORDS = ['italia','italy','it','roma','milano','torino','napoli','firenze']
const FULLSET_KEYWORDS = ['full set','box and papers','con scatola','con garanzia',
  'scatola e garanzia','b&p','b+p','completo','complete','box papers']

function matchesGeoFilter(l: WatchListing, f: 'all'|'italy'|'europe') {
  if (f === 'all') return true
  const loc = (l.location || '').toLowerCase().trim()
  if (f === 'italy') return loc === 'it' || ITALY_KEYWORDS.some(k => loc.includes(k))
  return EU_COUNTRIES.has(loc.toUpperCase()) || loc === '' || ITALY_KEYWORDS.some(k => loc.includes(k))
}

function matchesSetFilter(l: WatchListing, f: 'all'|'fullset'|'watchonly') {
  if (f === 'all') return true
  const text = ((l.description || '') + ' ' + (l.seller || '')).toLowerCase()
  const has = FULLSET_KEYWORDS.some(k => text.includes(k))
  return f === 'fullset' ? has : !has
}

function computeClientStats(listings: WatchListing[], reference: string): MarketStats | null {
  if (listings.length < 2) return null
  const prices = listings.map(l => l.price).sort((a, b) => a - b)
  const q1 = prices[Math.floor(prices.length * 0.25)]
  const q3 = prices[Math.floor(prices.length * 0.75)]
  const iqr = q3 - q1
  const clean = prices.filter(p => p >= q1 - 1.5 * iqr && p <= q3 + 1.5 * iqr)
  if (clean.length === 0) return null
  const pct = (arr: number[], p: number) => arr[Math.floor(arr.length * p)]
  const mean = clean.reduce((s, v) => s + v, 0) / clean.length
  const median = pct(clean, 0.5)
  const p25 = pct(clean, 0.25)
  const p75 = pct(clean, 0.75)
  return {
    reference,
    min_price: clean[0],
    max_price: clean[clean.length - 1],
    median_price: Math.round(median),
    mean_price: Math.round(mean),
    p25: Math.round(p25),
    p75: Math.round(p75),
    fair_price: Math.round(median * 0.6 + p25 * 0.4),
    sample_size: listings.length,
  }
}

function deriveInvestment(listings: WatchListing[], stats: MarketStats): InvestmentScore {
  const prices = listings.map(l => l.price)
  const mean = stats.mean_price
  const variance = prices.reduce((s, p) => s + Math.pow(p - mean, 2), 0) / prices.length
  const volatility = mean > 0 ? Math.min(1, Math.sqrt(variance) / mean) : 0
  const signal: InvestmentScore['signal'] =
    stats.fair_price < stats.median_price * 0.92 ? 'buy' :
    stats.fair_price < stats.median_price * 1.05 ? 'hold' : 'avoid'
  const liquidity: InvestmentScore['liquidity'] =
    listings.length >= 20 ? 'high' : listings.length >= 8 ? 'medium' : 'low'
  return {
    investment_score: Math.min(100, Math.round(
      (listings.length / 30) * 30 + (1 - volatility) * 40 +
      (signal === 'buy' ? 30 : signal === 'hold' ? 15 : 0)
    )),
    trend: 'stable',
    volatility,
    liquidity,
    signal,
  }
}

function ListingCard({ listing, isBest, isBestDeal = false }: {
  listing: WatchListing; isBest: boolean; isBestDeal?: boolean
}) {
  const { t, lang } = useLang()
  const sourceColor = SOURCE_COLORS[listing.source] || 'text-zinc-400 bg-zinc-400/10 border-zinc-400/20'
  const isSocial = ['instagram', 'vision_ai', 'tiktok', 'instagram_story'].includes(listing.source)
  const conditionLabels = lang === 'it'
    ? { new: 'Nuovo', mint: 'Perfetto', good: 'Buono', fair: 'Discreto', unknown: 'N/D' }
    : { new: 'New', mint: 'Mint', good: 'Good', fair: 'Fair', unknown: 'N/A' }
  const conditionLabel = (conditionLabels as Record<string,string>)[listing.condition] ?? listing.condition

  return (
    <a
      href={listing.url}
      target="_blank"
      rel="noopener noreferrer"
      className={clsx(
        'group relative flex gap-8 p-6 transition-all',
        isBest
          ? 'bg-zinc-900 border-2 border-primary'
          : 'bg-zinc-900 border border-zinc-800 hover:border-zinc-700'
      )}
    >
      {isBest && (
        <div className="absolute -top-3 left-6 bg-primary text-zinc-950 px-3 py-0.5 text-[10px] font-bold uppercase tracking-widest flex items-center gap-1">
          <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
          {t.bestPrice}
        </div>
      )}
      {!isBest && isBestDeal && (
        <div className="absolute -top-3 left-6 bg-orange-500 text-zinc-950 px-3 py-0.5 text-[10px] font-bold uppercase tracking-widest">
          {t.bestDeal}
        </div>
      )}

      {/* Image placeholder */}
      <div className="w-48 h-48 bg-zinc-950 border border-zinc-800 overflow-hidden flex-shrink-0 flex items-center justify-center grayscale group-hover:grayscale-0 transition-all">
        <span className="material-symbols-outlined text-5xl text-zinc-700">watch</span>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex justify-between items-start gap-4">
          <div className="min-w-0">
            {isBest && (
              <span className="text-[10px] uppercase tracking-widest text-primary font-bold mb-1 block">{t.topRanked}</span>
            )}
            <h3 className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-lg leading-tight truncate">
              {listing.seller}
            </h3>
            <p className="text-zinc-500 text-sm mt-1 truncate">
              {conditionLabel}
              {listing.description ? ` • ${listing.description}` : ''}
            </p>
          </div>
          <div className="text-right shrink-0">
            <span className={clsx('font-display-price text-3xl leading-none', isBest ? 'text-zinc-100' : 'text-zinc-100')}>
              {listing.price.toLocaleString('it-IT')} €
            </span>
            <p className="text-zinc-500 text-xs mt-1 uppercase tracking-tight">
              {isSocial ? t.socialVerified : t.marketPrice}
            </p>
          </div>
        </div>

        <div className="mt-auto flex items-center justify-between border-t border-zinc-800 pt-4">
          <div className="flex gap-4 flex-wrap">
            <span className={clsx('px-2 py-1 text-[10px] font-bold uppercase border', sourceColor)}>
              {SOURCE_LABELS[listing.source] || listing.source}
            </span>
            {listing.location && (
              <span className="flex items-center gap-1 text-zinc-500 text-xs">
                <span className="material-symbols-outlined text-sm leading-none">location_on</span>
                {listing.location}
              </span>
            )}
            <span className="flex items-center gap-1 text-zinc-500 text-xs">
              <span className="material-symbols-outlined text-sm leading-none">schedule</span>
              {formatDistanceToNow(new Date(listing.scraped_at), { addSuffix: true, locale: itLocale })}
            </span>
          </div>
          <button className={clsx(
            'px-6 py-2 text-xs font-bold uppercase tracking-widest transition-colors shrink-0',
            isBest ? 'bg-primary text-zinc-950 hover:bg-yellow-300' : 'bg-zinc-800 text-zinc-100 hover:bg-zinc-700'
          )}>
            {isSocial ? t.contactSeller : t.viewDetails}
          </button>
        </div>
      </div>
    </a>
  )
}

function saveRecentSearch(ref: string) {
  try {
    const prev: { ref: string; ts: number }[] = JSON.parse(sessionStorage.getItem('recentSearches') || '[]')
    const next = [{ ref, ts: Date.now() }, ...prev.filter(r => r.ref !== ref)].slice(0, 8)
    sessionStorage.setItem('recentSearches', JSON.stringify(next))
  } catch { /* ignore */ }
}

export default function SearchPage() {
  const [params] = useSearchParams()
  const { t } = useLang()
  const [reference, setReference] = useState(params.get('ref') || '')
  const [maxPrice, setMaxPrice] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [scanStep, setScanStep] = useState(0)
  const [filterGeo, setFilterGeo] = useState<'all'|'italy'|'europe'>('all')
  const [filterSet, setFilterSet] = useState<'all'|'fullset'|'watchonly'>('all')
  const [filterSeller, setFilterSeller] = useState('')
  const [filterPriceMin, setFilterPriceMin] = useState('')
  const [filterPriceMax, setFilterPriceMax] = useState('')
  const [filterSources, setFilterSources] = useState<Set<string>>(new Set())
  const scanStepRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [identifying, setIdentifying] = useState(false)
  const [identifyResult, setIdentifyResult] = useState<{brand:string|null;model:string|null;reference:string|null;confidence:number;notes:string|null}|null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: scanWatch,
    onSuccess: (data) => {
      if (scanStepRef.current) clearTimeout(scanStepRef.current)
      setScanStep(SCAN_STEPS.length)
      setResult(data)
      setError(null)
    },
    onError: (err: any) => {
      if (scanStepRef.current) clearTimeout(scanStepRef.current)
      setScanStep(0)
      setError(err?.response?.data?.detail || err?.message || 'Errore durante la scansione')
    },
  })

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIdentifying(true)
    setIdentifyResult(null)
    try {
      const r = await identifyWatchFromImage(file)
      if (r.identified) {
        setIdentifyResult(r)
        if (r.reference) setReference(r.reference)
      } else {
        setIdentifyResult({ brand:null, model:null, reference:null, confidence:0, notes:'Orologio non riconosciuto' })
      }
    } catch {
      setIdentifyResult({ brand:null, model:null, reference:null, confidence:0, notes:'Errore durante il riconoscimento' })
    } finally {
      setIdentifying(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleScan = (ref?: string) => {
    const target = (ref ?? reference).trim()
    if (!target) return
    if (ref) setReference(ref)
    saveRecentSearch(target.toUpperCase())
    setError(null); setResult(null); setScanStep(0)
    setFilterGeo('all'); setFilterSet('all'); setFilterSeller('')
    setFilterPriceMin(''); setFilterPriceMax(''); setFilterSources(new Set())
    let step = 0
    const advance = () => {
      step += 1
      if (step < SCAN_STEPS.length) {
        setScanStep(step)
        scanStepRef.current = setTimeout(advance, SCAN_DURATIONS[step])
      }
    }
    scanStepRef.current = setTimeout(advance, SCAN_DURATIONS[0])
    mutate({ reference: target.toUpperCase(), max_price: maxPrice ? parseFloat(maxPrice) : undefined })
  }

  useEffect(() => {
    const ref = params.get('ref')
    if (ref) { setReference(ref); mutate({ reference: ref.toUpperCase() }) }
  }, [])

  const filteredListings = result ? result.listings.filter(l =>
    matchesGeoFilter(l, filterGeo) &&
    matchesSetFilter(l, filterSet) &&
    (!filterSeller || l.seller.toLowerCase().includes(filterSeller.toLowerCase()) ||
     (l.description || '').toLowerCase().includes(filterSeller.toLowerCase())) &&
    (!filterPriceMin || l.price >= parseFloat(filterPriceMin)) &&
    (!filterPriceMax || l.price <= parseFloat(filterPriceMax)) &&
    (filterSources.size === 0 || filterSources.has(l.source))
  ) : []

  const sourceCounts = result ? result.listings.reduce((acc, l) => {
    acc[l.source] = (acc[l.source] || 0) + 1
    return acc
  }, {} as Record<string, number>) : {}

  const clientStats = result && result.listings.length >= 2
    ? computeClientStats(result.listings, result.query.reference) : null
  const clientInvestment = clientStats ? deriveInvestment(result!.listings, clientStats) : null
  const medianForDeal = clientStats?.median_price ?? 0

  const { data: priceHistory = [] } = useQuery({
    queryKey: ['price-history', result?.query.reference],
    queryFn: () => getPriceHistory(result!.query.reference, 365 * 20),
    enabled: !!result?.query.reference,
    staleTime: 5 * 60 * 1000,
  })

  const progressPercent = (scanStep / SCAN_STEPS.length) * 100

  return (
    <div className="p-8 max-w-[1400px] mx-auto">

      {/* ── Breadcrumb + Title ── */}
      <div className="flex items-end justify-between mb-8">
        <div>
          <nav className="flex text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2 gap-2">
            <span className="hover:text-yellow-400 cursor-pointer">{t.marketIntelligence}</span>
            <span>/</span>
            <span className="text-zinc-300">{t.scanTerminal}</span>
          </nav>
          <h2 className="font-h1 text-h1 text-zinc-100">{t.scanTerminal}</h2>
        </div>
        {result && (
          <div className="flex bg-zinc-900 border border-zinc-800 p-1 rounded">
            <button className="px-4 py-1.5 text-xs font-bold bg-zinc-800 text-yellow-400 rounded">Live</button>
          </div>
        )}
      </div>

      {/* ── Search form ── */}
      <div className="bg-zinc-900 border border-zinc-800 p-[24px] mb-8">

        <div className="flex items-center justify-between mb-4">
          <label className="font-label-caps text-label-caps text-zinc-400 uppercase flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm leading-none text-yellow-400">watch</span>
            {t.referenceLabel}
          </label>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={identifying || isPending}
            className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-yellow-400 transition-colors disabled:opacity-40"
          >
            {identifying
              ? <span className="material-symbols-outlined text-sm leading-none animate-spin">autorenew</span>
              : <span className="material-symbols-outlined text-sm leading-none">photo_camera</span>}
            {identifying ? t.identifying : t.scanFromPhoto}
          </button>
        </div>
        <input type="file" ref={fileInputRef} accept="image/*" onChange={handleImageUpload} className="hidden" />

        <input
          value={reference}
          onChange={e => setReference(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleScan()}
          placeholder={t.referencePlaceholder}
          className="w-full bg-zinc-800 border border-zinc-700 rounded px-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-yellow-400 transition-colors text-base mb-4"
        />

        {identifyResult && (
          <div className={clsx(
            'flex items-start justify-between gap-3 p-3 mb-4 text-xs border rounded',
            identifyResult.confidence > 0.3
              ? 'bg-green-900/20 border-green-700/40 text-green-300'
              : 'bg-zinc-800 border-zinc-700 text-zinc-400'
          )}>
            <div>
              {identifyResult.confidence > 0.3 ? (
                <>
                  <p className="font-semibold mb-0.5">
                    {[identifyResult.brand, identifyResult.model].filter(Boolean).join(' ')}
                    {identifyResult.reference && <span className="ml-1 text-yellow-400">· {identifyResult.reference}</span>}
                  </p>
                  {identifyResult.notes && <p className="text-zinc-500">{identifyResult.notes}</p>}
                </>
              ) : (
                <p>{identifyResult.notes}</p>
              )}
            </div>
            <button onClick={() => setIdentifyResult(null)} className="shrink-0 text-zinc-600 hover:text-zinc-300">
              <span className="material-symbols-outlined text-sm leading-none">close</span>
            </button>
          </div>
        )}

        <div className="flex gap-3 items-end mb-4">
          <div className="w-44">
            <label className="font-label-caps text-[11px] text-zinc-500 uppercase mb-2 block">{t.maxPriceLabel}</label>
            <input
              value={maxPrice}
              onChange={e => setMaxPrice(e.target.value)}
              placeholder={t.maxPricePlaceholder}
              type="number"
              className="w-full bg-zinc-800 border border-zinc-700 rounded px-4 py-2.5 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-yellow-400 transition-colors text-sm"
            />
          </div>
          <button
            onClick={() => handleScan()}
            disabled={isPending || !reference.trim()}
            className={clsx(
              'flex-1 flex items-center justify-center gap-2 rounded px-6 py-2.5 font-bold text-sm uppercase tracking-widest transition-all',
              'bg-primary text-on-primary hover:opacity-90',
              'disabled:opacity-40 disabled:cursor-not-allowed'
            )}
          >
            {isPending
              ? <span className="material-symbols-outlined text-base leading-none animate-spin">autorenew</span>
              : <span className="material-symbols-outlined text-base leading-none">search</span>}
            {isPending ? t.scanningButton : t.scanButton}
          </button>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-label-caps text-[11px] text-zinc-500 uppercase">{t.quickSearch}</span>
          {QUICK_REFS.map(ref => (
            <button
              key={ref}
              onClick={() => handleScan(ref)}
              disabled={isPending}
              className="text-xs px-3 py-1 rounded bg-zinc-800 border border-zinc-700 text-zinc-400 hover:border-yellow-400/50 hover:text-yellow-400 transition-all disabled:opacity-40"
            >
              {ref}
            </button>
          ))}
        </div>
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="flex items-start gap-3 bg-red-900/20 border border-red-700/40 p-4 mb-6 text-red-300 text-sm rounded">
          <span className="material-symbols-outlined text-lg leading-none text-red-400 shrink-0">warning</span>
          <span>{error}</span>
        </div>
      )}

      {/* ── Loading ── */}
      {isPending && (
        <div className="bg-zinc-900 border border-zinc-800 p-[24px]">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-2xl text-yellow-400 animate-spin">autorenew</span>
            <div>
              <p className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-sm">
                {t.scanningFor} <span className="text-yellow-400">{reference.toUpperCase()}</span>
              </p>
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-0.5">{t.agentsActive}</p>
            </div>
          </div>

          <div className="space-y-2 mb-6">
            {SCAN_STEPS.map((step, i) => {
              const done = i < scanStep
              const active = i === scanStep
              return (
                <div key={i} className={clsx(
                  'flex items-center gap-3 px-3 py-2.5 transition-all',
                  active && 'bg-yellow-400/5 border border-yellow-400/15',
                  done && 'opacity-50'
                )}>
                  <span className={clsx('material-symbols-outlined text-base leading-none shrink-0',
                    done ? 'text-green-400' : active ? 'text-yellow-400 animate-spin' : 'text-zinc-700'
                  )}>
                    {done ? 'check_circle' : active ? 'autorenew' : 'radio_button_unchecked'}
                  </span>
                  <span className={clsx('material-symbols-outlined text-sm leading-none shrink-0',
                    done ? 'text-green-500' : active ? 'text-yellow-400' : 'text-zinc-700'
                  )}>{step.icon}</span>
                  <span className={clsx('text-sm flex-1',
                    done ? 'text-zinc-500 line-through decoration-zinc-700' : active ? 'text-zinc-100 font-medium' : 'text-zinc-600'
                  )}>{step.label}</span>
                  {done && <span className="text-xs text-green-500 font-medium">Fatto</span>}
                </div>
              )
            })}
          </div>

          <div className="w-full bg-zinc-800 h-1">
            <div className="bg-yellow-400 h-1 transition-all duration-700" style={{ width: `${progressPercent}%` }} />
          </div>
          <p className="text-[10px] text-zinc-600 uppercase tracking-widest mt-3 text-center">
            {t.scanDuration}
          </p>
        </div>
      )}

      {/* ── Results ── */}
      {result && !isPending && (
        <div>
          {clientStats && clientInvestment && (
            <MarketCard stats={clientStats} investment={clientInvestment} />
          )}
          {clientStats && (
            <PriceEvolutionChart
              history={priceHistory}
              fairPrice={clientStats.fair_price}
              reference={result.query.reference}
            />
          )}

          {/* Results header */}
          <section className="py-6 flex items-baseline justify-between">
            <div>
              <h2 className="font-h1 text-h1 text-on-surface">{result.query.reference}</h2>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-label-caps font-label-caps text-zinc-500">
                  {filteredListings.length} {t.resultsFound}
                </span>
                <span className="w-1 h-1 bg-zinc-700 rounded-full" />
                <span className="text-label-caps font-label-caps text-primary">{t.liveMarketFeed}</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-4 py-2 text-xs font-label-caps uppercase text-zinc-400 hover:bg-zinc-800 transition-colors">
                <span className="material-symbols-outlined text-sm">sort</span> {t.sortPrice}
              </button>
              <button className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-4 py-2 text-xs font-label-caps uppercase text-zinc-400 hover:bg-zinc-800 transition-colors">
                <span className="material-symbols-outlined text-sm">grid_view</span>
              </button>
            </div>
          </section>

          {/* Two-column layout: filters + results */}
          <div className="flex gap-8 pb-12">

            {/* Filter sidebar */}
            <aside className="w-64 flex-shrink-0">
              <div className="space-y-8">

                {/* Price Range */}
                <div>
                  <h3 className="text-label-caps font-label-caps text-zinc-300 mb-4 border-b border-zinc-800 pb-2">{t.priceRange}</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      className="bg-zinc-900 border border-zinc-800 p-2 text-xs font-mono-data text-zinc-200 rounded focus:outline-none focus:border-primary"
                      placeholder="Min"
                      type="text"
                      value={filterPriceMin}
                      onChange={e => setFilterPriceMin(e.target.value)}
                    />
                    <input
                      className="bg-zinc-900 border border-zinc-800 p-2 text-xs font-mono-data text-zinc-200 rounded focus:outline-none focus:border-primary"
                      placeholder="Max"
                      type="text"
                      value={filterPriceMax}
                      onChange={e => setFilterPriceMax(e.target.value)}
                    />
                  </div>
                </div>

                {/* Accessories */}
                <div>
                  <h3 className="text-label-caps font-label-caps text-zinc-300 mb-4 border-b border-zinc-800 pb-2">{t.accessories}</h3>
                  <div className="space-y-2">
                    {(['all', 'fullset', 'watchonly'] as const).map(opt => (
                      <label key={opt} className="flex items-center gap-3 text-sm text-zinc-400 cursor-pointer">
                        <input
                          type="radio"
                          name="filterSet"
                          checked={filterSet === opt}
                          onChange={() => setFilterSet(opt)}
                          className="rounded border-zinc-700 bg-zinc-800 text-primary focus:ring-0"
                        />
                        {opt === 'all' ? t.allAccessories : opt === 'fullset' ? t.boxPapers : t.watchOnly}
                      </label>
                    ))}
                  </div>
                </div>

                {/* Location */}
                <div>
                  <h3 className="text-label-caps font-label-caps text-zinc-300 mb-4 border-b border-zinc-800 pb-2">{t.location}</h3>
                  <div className="space-y-2">
                    {(['all', 'italy', 'europe'] as const).map(opt => (
                      <label key={opt} className="flex items-center gap-3 text-sm text-zinc-400 cursor-pointer">
                        <input
                          type="radio"
                          name="filterGeo"
                          checked={filterGeo === opt}
                          onChange={() => setFilterGeo(opt)}
                          className="rounded border-zinc-700 bg-zinc-800 text-primary focus:ring-0"
                        />
                        {opt === 'all' ? t.worldwide : opt === 'italy' ? t.italy : t.europe}
                      </label>
                    ))}
                  </div>
                  <div className="relative mt-3">
                    <input
                      className="w-full bg-zinc-900 border border-zinc-800 p-2 text-xs font-mono-data text-zinc-200 rounded pl-8 focus:outline-none focus:border-primary"
                      placeholder={t.filterSeller}
                      type="text"
                      value={filterSeller}
                      onChange={e => setFilterSeller(e.target.value)}
                    />
                    <span className="material-symbols-outlined absolute left-2 top-1/2 -translate-y-1/2 text-zinc-600 text-sm">search</span>
                  </div>
                </div>

                {/* Market Source */}
                <div>
                  <h3 className="text-label-caps font-label-caps text-zinc-300 mb-4 border-b border-zinc-800 pb-2">{t.marketSource}</h3>
                  <div className="space-y-2">
                    {Object.entries(sourceCounts).map(([src, count]) => (
                      <label key={src} className="flex items-center justify-between text-sm text-zinc-400 cursor-pointer">
                        <span className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={filterSources.size === 0 || filterSources.has(src)}
                            onChange={() => {
                              setFilterSources(prev => {
                                const next = new Set(prev.size === 0 ? Object.keys(sourceCounts) : prev)
                                if (next.has(src)) next.delete(src)
                                else next.add(src)
                                if (next.size === Object.keys(sourceCounts).length) return new Set()
                                return next
                              })
                            }}
                            className="rounded border-zinc-700 bg-zinc-800 text-primary focus:ring-0"
                          />
                          {SOURCE_LABELS[src] || src}
                        </span>
                        <span className="text-[10px] text-zinc-600">{count}</span>
                      </label>
                    ))}
                  </div>
                </div>

              </div>
            </aside>

            {/* Results grid */}
            <div className="flex-1 space-y-4">
              {filteredListings.length === 0 ? (
                <div className="text-center py-16 bg-zinc-900 border border-zinc-800">
                  <span className="material-symbols-outlined text-5xl text-zinc-700 block mb-4">search_off</span>
                  <p className="font-['Space_Grotesk'] font-semibold text-zinc-300 mb-2">
                    {result.listings.length === 0
                      ? `${t.noListings} ${result.query.reference}`
                      : t.noResults}
                  </p>
                  <p className="text-sm text-zinc-600">
                    {result.listings.length === 0
                      ? t.noListingsSub
                      : t.noResultsSub}
                  </p>
                </div>
              ) : (
                filteredListings.map((listing, i) => (
                  <ListingCard
                    key={`${listing.source}-${listing.url}-${i}`}
                    listing={listing}
                    isBest={i === 0}
                    isBestDeal={medianForDeal > 0 && listing.price < medianForDeal * 0.90}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
