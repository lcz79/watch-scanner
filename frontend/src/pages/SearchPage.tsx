import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Search,
  Loader2,
  ExternalLink,
  MapPin,
  Tag,
  Clock,
  CheckCircle2,
  Circle,
  Watch,
  AlertTriangle,
  Zap,
  Globe,
  BarChart2,
  Wifi,
  Camera,
  X,
} from 'lucide-react'
import { scanWatch, getPriceHistory, identifyWatchFromImage } from '../lib/api'
import type { WatchListing, ScanResult, MarketStats, InvestmentScore } from '../types'
import MarketCard from '../components/MarketCard'
import PriceEvolutionChart from '../components/PriceEvolutionChart'
import { clsx } from 'clsx'
import { formatDistanceToNow } from 'date-fns'
import { it } from 'date-fns/locale'

// ─── Constants ────────────────────────────────────────────────────────────────

const QUICK_REFS = ['116610LN', '126710BLNR', '5711/1A', '116500LN', '15500ST']

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
  { label: 'Connessione agli agenti', icon: Wifi, duration: 3000 },
  { label: 'Scansione Chrono24', icon: Globe, duration: 15000 },
  { label: 'Scansione eBay', icon: Tag, duration: 8000 },
  { label: 'Analisi Instagram + Subito.it', icon: Zap, duration: 10000 },
  { label: 'Aggregazione risultati', icon: BarChart2, duration: 4000 },
]

// ─── Geo / Set filter helpers ─────────────────────────────────────────────────

const EU_COUNTRIES = new Set(['IT','DE','FR','ES','NL','BE','AT','CH','PT','PL',
  'SE','NO','DK','FI','CZ','HU','RO','GR','SK','HR','SI','LU','IE','BG','LV',
  'LT','EE','MT','CY','GB','UK'])

const ITALY_KEYWORDS = ['italia','italy','it','roma','milano','torino','napoli','firenze']

const FULLSET_KEYWORDS = ['full set','box and papers','con scatola','con garanzia',
  'scatola e garanzia','b&p','b+p','completo','complete','box papers']

function matchesGeoFilter(listing: WatchListing, filter: 'all' | 'italy' | 'europe'): boolean {
  if (filter === 'all') return true
  const loc = (listing.location || '').toLowerCase().trim()
  if (filter === 'italy') {
    return loc === 'it' || ITALY_KEYWORDS.some(k => loc.includes(k))
  }
  if (filter === 'europe') {
    return EU_COUNTRIES.has(loc.toUpperCase()) ||
           loc === '' ||
           ITALY_KEYWORDS.some(k => loc.includes(k))
  }
  return true
}

function matchesSetFilter(listing: WatchListing, filter: 'all' | 'fullset' | 'watchonly'): boolean {
  if (filter === 'all') return true
  const text = ((listing.description || '') + ' ' + (listing.seller || '')).toLowerCase()
  const hasFullSet = FULLSET_KEYWORDS.some(k => text.includes(k))
  if (filter === 'fullset') return hasFullSet
  if (filter === 'watchonly') return !hasFullSet
  return true
}

// ─── Client-side market stats ─────────────────────────────────────────────────

function computeClientStats(listings: WatchListing[], reference: string): MarketStats | null {
  if (listings.length < 2) return null

  const prices = listings.map(l => l.price).sort((a, b) => a - b)

  // IQR outlier removal
  const q1 = prices[Math.floor(prices.length * 0.25)]
  const q3 = prices[Math.floor(prices.length * 0.75)]
  const iqr = q3 - q1
  const clean = prices.filter(p => p >= q1 - 1.5 * iqr && p <= q3 + 1.5 * iqr)

  if (clean.length === 0) return null

  const pct = (arr: number[], p: number) => arr[Math.floor(arr.length * p)]
  const mean = clean.reduce((s, v) => s + v, 0) / clean.length
  const median = pct(clean, 0.5)
  const p25   = pct(clean, 0.25)
  const p75   = pct(clean, 0.75)
  // Fair price: weighted blend of median (60%) and p25 (40%) to lean towards value
  const fairPrice = Math.round(median * 0.6 + p25 * 0.4)

  return {
    reference,
    min_price:    clean[0],
    max_price:    clean[clean.length - 1],
    median_price: Math.round(median),
    mean_price:   Math.round(mean),
    p25:          Math.round(p25),
    p75:          Math.round(p75),
    fair_price:   fairPrice,
    sample_size:  listings.length,
  }
}


function deriveInvestment(listings: WatchListing[], stats: MarketStats): InvestmentScore {
  const prices = listings.map(l => l.price)
  const mean = stats.mean_price
  const variance = prices.reduce((s, p) => s + Math.pow(p - mean, 2), 0) / prices.length
  const stdDev = Math.sqrt(variance)
  const volatility = mean > 0 ? Math.min(1, stdDev / mean) : 0

  const signal: InvestmentScore['signal'] =
    stats.fair_price < stats.median_price * 0.92 ? 'buy' :
    stats.fair_price < stats.median_price * 1.05 ? 'hold' : 'avoid'

  const liquidity: InvestmentScore['liquidity'] =
    listings.length >= 20 ? 'high' : listings.length >= 8 ? 'medium' : 'low'

  const investment_score = Math.min(100, Math.round(
    (listings.length / 30) * 30 +          // liquidity component (max 30)
    (1 - volatility) * 40 +                // stability component (max 40)
    (signal === 'buy' ? 30 : signal === 'hold' ? 15 : 0) // signal component
  ))

  return {
    investment_score,
    trend: 'stable',
    volatility,
    liquidity,
    signal,
  }
}

// ─── ListingCard ───────────────────────────────────────────────────────────────

function ListingCard({
  listing,
  isBest,
  isBestDeal = false,
}: {
  listing: WatchListing
  isBest: boolean
  isBestDeal?: boolean
}) {
  const color = SOURCE_COLORS[listing.source] || 'text-zinc-400 bg-zinc-400/10 border-zinc-400/20'

  return (
    <a
      href={listing.url}
      target="_blank"
      rel="noopener noreferrer"
      className={clsx(
        'group block rounded-xl border p-5 transition-all duration-200',
        'hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/40',
        isBest
          ? 'bg-zinc-900 border-gold-400/50 ring-1 ring-gold-400/10 hover:border-gold-400/70'
          : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
      )}
    >
      {/* Badges row */}
      {(isBest || isBestDeal) && (
        <div className="mb-3 flex items-center gap-2 flex-wrap">
          {isBest && (
            <div className="inline-flex items-center gap-1.5 rounded-full bg-gold-400/10 border border-gold-400/30 px-3 py-1">
              <span className="text-gold-400 text-xs">★</span>
              <span className="text-xs font-semibold text-gold-400 tracking-wide uppercase">Miglior prezzo</span>
            </div>
          )}
          {isBestDeal && (
            <div className="inline-flex items-center gap-1.5 rounded-full bg-orange-500/15 border border-orange-500/30 px-3 py-1">
              <span className="text-orange-400 text-xs">🔥</span>
              <span className="text-xs font-semibold text-orange-400 tracking-wide uppercase">Miglior Affare</span>
            </div>
          )}
        </div>
      )}

      <div className="flex items-start justify-between gap-4">
        {/* Left: meta */}
        <div className="flex-1 min-w-0">
          {/* Badges row */}
          <div className="flex items-center gap-2 mb-2.5 flex-wrap">
            <span className={clsx('text-xs border rounded-full px-2.5 py-0.5 font-medium', color)}>
              {SOURCE_LABELS[listing.source] || listing.source}
            </span>
            <span className="text-xs text-zinc-400 bg-zinc-800 border border-zinc-700 rounded-full px-2.5 py-0.5 capitalize">
              {({
                new: 'Nuovo',
                mint: 'Perfetto',
                good: 'Buono',
                fair: 'Discreto',
                unknown: 'Non specificato',
              } as Record<string, string>)[listing.condition] ?? listing.condition}
            </span>
          </div>

          {/* Seller */}
          <p className="font-semibold text-zinc-100 truncate text-sm">{listing.seller}</p>

          {/* Description */}
          {listing.description && (
            <p className="text-xs text-zinc-500 mt-1 truncate">{listing.description}</p>
          )}

          {/* Location + timestamp */}
          <div className="flex items-center gap-3 mt-2.5">
            {listing.location && (
              <span className="flex items-center gap-1 text-xs text-zinc-500">
                <MapPin size={11} />
                {listing.location}
              </span>
            )}
            <span className="flex items-center gap-1 text-xs text-zinc-600">
              <Clock size={11} />
              {formatDistanceToNow(new Date(listing.scraped_at), { addSuffix: true, locale: it })}
            </span>
          </div>
        </div>

        {/* Right: price + link */}
        <div className="text-right shrink-0 flex flex-col items-end gap-2">
          <p
            className={clsx(
              'font-display font-bold text-2xl',
              isBest ? 'text-gold-400' : 'text-zinc-100'
            )}
          >
            {listing.price.toLocaleString('it-IT')} €
          </p>
          <ExternalLink
            size={14}
            className="text-zinc-700 group-hover:text-zinc-400 transition-colors"
          />
        </div>
      </div>
    </a>
  )
}

// ─── SearchPage ────────────────────────────────────────────────────────────────

export default function SearchPage() {
  const [params] = useSearchParams()
  const [reference, setReference] = useState(params.get('ref') || '')
  const [maxPrice, setMaxPrice] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [scanStep, setScanStep] = useState(0)
  const [filterGeo, setFilterGeo] = useState<'all' | 'italy' | 'europe'>('all')
  const [filterSet, setFilterSet] = useState<'all' | 'fullset' | 'watchonly'>('all')
  const [filterSeller, setFilterSeller] = useState('')
  const scanStepRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [identifying, setIdentifying] = useState(false)
  const [identifyResult, setIdentifyResult] = useState<{brand:string|null, model:string|null, reference:string|null, confidence:number, notes:string|null} | null>(null)
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
      const result = await identifyWatchFromImage(file)
      if (result.identified) {
        setIdentifyResult(result)
        if (result.reference) {
          setReference(result.reference)
        }
      } else {
        setIdentifyResult({ brand: null, model: null, reference: null, confidence: 0, notes: 'Orologio non riconosciuto' })
      }
    } catch {
      setIdentifyResult({ brand: null, model: null, reference: null, confidence: 0, notes: 'Errore durante il riconoscimento' })
    } finally {
      setIdentifying(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleScan = (ref?: string) => {
    const target = (ref ?? reference).trim()
    if (!target) return
    if (ref) setReference(ref)
    setError(null)
    setResult(null)
    setScanStep(0)
    setFilterGeo('all')
    setFilterSet('all')
    setFilterSeller('')

    let step = 0
    const advance = () => {
      step += 1
      if (step < SCAN_STEPS.length) {
        setScanStep(step)
        scanStepRef.current = setTimeout(advance, SCAN_STEPS[step].duration)
      }
    }
    scanStepRef.current = setTimeout(advance, SCAN_STEPS[0].duration)

    mutate({
      reference: target.toUpperCase(),
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
    })
  }

  useEffect(() => {
    const ref = params.get('ref')
    if (ref) {
      setReference(ref)
      mutate({ reference: ref.toUpperCase() })
    }
  }, [])

  const progressPercent = (scanStep / SCAN_STEPS.length) * 100

  const filteredListings = result ? result.listings.filter(l =>
    matchesGeoFilter(l, filterGeo) &&
    matchesSetFilter(l, filterSet) &&
    (!filterSeller || l.seller.toLowerCase().includes(filterSeller.toLowerCase()) || (l.description || '').toLowerCase().includes(filterSeller.toLowerCase()))
  ) : []

  // Client-side market intelligence
  const clientStats = result && result.listings.length >= 2
    ? computeClientStats(result.listings, result.query.reference)
    : null
  const clientInvestment = clientStats
    ? deriveInvestment(result!.listings, clientStats)
    : null

  // Price history from backend (for PriceEvolutionChart)
  const { data: priceHistory = [] } = useQuery({
    queryKey: ['price-history', result?.query.reference],
    queryFn: () => getPriceHistory(result!.query.reference, 365 * 20),
    enabled: !!result?.query.reference,
    staleTime: 5 * 60 * 1000,
  })

  // Best deal threshold: price < median * 0.90
  const medianForDeal = clientStats?.median_price ?? 0

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">

      {/* ── Page title ── */}
      <div className="mb-10">
        <h1 className="font-display font-bold text-3xl text-zinc-100 tracking-tight">
          Cerca referenza
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Scansione in tempo reale su marketplace e social media
        </p>
      </div>

      {/* ── Search form ── */}
      <div className="bg-zinc-900 border border-gold-400/20 rounded-2xl p-6 mb-8 shadow-lg shadow-black/30">
        {/* Reference input */}
        <div className="mb-4">
          <label className="flex items-center justify-between text-xs font-medium text-zinc-400 mb-2">
            <span className="flex items-center gap-1.5">
              <Watch size={13} className="text-gold-400" />
              Referenza orologio
            </span>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={identifying || isPending}
              className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-gold-400 transition-colors disabled:opacity-40"
            >
              {identifying ? <Loader2 size={13} className="animate-spin" /> : <Camera size={13} />}
              {identifying ? 'Identificazione…' : 'Cerca da foto'}
            </button>
          </label>
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
          <input
            value={reference}
            onChange={e => setReference(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleScan()}
            placeholder="es. 116610LN · 5711/1A · 126710BLNR"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3.5 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-gold-400 focus:ring-1 focus:ring-gold-400/30 transition-all text-base"
          />
        </div>

        {identifyResult && (
          <div className={clsx(
            'flex items-start justify-between gap-3 rounded-xl p-3 mb-4 text-xs border',
            identifyResult.confidence > 0.3
              ? 'bg-green-900/20 border-green-700/40 text-green-300'
              : 'bg-zinc-800 border-zinc-700 text-zinc-400'
          )}>
            <div>
              {identifyResult.confidence > 0.3 ? (
                <>
                  <p className="font-semibold mb-0.5">
                    {[identifyResult.brand, identifyResult.model].filter(Boolean).join(' ')}
                    {identifyResult.reference && <span className="ml-1 text-gold-400">· {identifyResult.reference}</span>}
                  </p>
                  {identifyResult.notes && <p className="text-zinc-500">{identifyResult.notes}</p>}
                  {identifyResult.reference && (
                    <p className="text-green-400 mt-1">Referenza inserita automaticamente ↑</p>
                  )}
                </>
              ) : (
                <p>{identifyResult.notes || 'Orologio non riconosciuto'}</p>
              )}
            </div>
            <button onClick={() => setIdentifyResult(null)} className="shrink-0 text-zinc-600 hover:text-zinc-300">
              <X size={14} />
            </button>
          </div>
        )}

        {/* Max price + button row */}
        <div className="flex gap-3 items-end">
          <div className="w-44">
            <label className="text-xs font-medium text-zinc-500 mb-2 block">
              Prezzo max (€) — opzionale
            </label>
            <input
              value={maxPrice}
              onChange={e => setMaxPrice(e.target.value)}
              placeholder="es. 12000"
              type="number"
              className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-gold-400 focus:ring-1 focus:ring-gold-400/30 transition-all text-sm"
            />
          </div>
          <button
            onClick={() => handleScan()}
            disabled={isPending || !reference.trim()}
            className={clsx(
              'flex-1 flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold text-sm transition-all duration-200',
              'bg-gold-400 text-zinc-900 hover:bg-gold-500',
              'disabled:opacity-40 disabled:cursor-not-allowed',
              'shadow-md shadow-gold-400/10'
            )}
          >
            {isPending ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Search size={18} />
            )}
            {isPending ? 'Scansione in corso…' : 'Scansiona'}
          </button>
        </div>

        {/* Quick refs */}
        <div className="mt-4 flex items-center gap-2 flex-wrap">
          <span className="text-xs text-zinc-600">Rapido:</span>
          {QUICK_REFS.map(ref => (
            <button
              key={ref}
              onClick={() => handleScan(ref)}
              disabled={isPending}
              className="text-xs px-3 py-1 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-400 hover:border-gold-400/50 hover:text-gold-400 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {ref}
            </button>
          ))}
        </div>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="flex items-start gap-3 bg-red-900/20 border border-red-700/40 rounded-xl p-4 mb-6 text-red-300 text-sm">
          <AlertTriangle size={16} className="shrink-0 mt-0.5 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* ── Loading state ── */}
      {isPending && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
          {/* Header */}
          <div className="flex items-center gap-3 mb-7">
            <div className="relative flex items-center justify-center w-8 h-8">
              <Loader2 size={22} className="animate-spin text-gold-400" />
            </div>
            <div>
              <p className="font-semibold text-zinc-100 text-sm">
                Scansione in corso per{' '}
                <span className="text-gold-400">{reference.toUpperCase()}</span>
              </p>
              <p className="text-xs text-zinc-600 mt-0.5">Agenti in parallelo attivi</p>
            </div>
          </div>

          {/* Steps */}
          <div className="space-y-3 mb-7">
            {SCAN_STEPS.map((step, i) => {
              const done = i < scanStep
              const active = i === scanStep
              const StepIcon = step.icon
              return (
                <div
                  key={i}
                  className={clsx(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all duration-300',
                    active && 'bg-gold-400/5 border border-gold-400/15',
                    done && 'opacity-60'
                  )}
                >
                  {/* Status icon */}
                  <div className="shrink-0 w-5 h-5 flex items-center justify-center">
                    {done ? (
                      <CheckCircle2 size={18} className="text-green-400" />
                    ) : active ? (
                      <Loader2 size={18} className="animate-spin text-gold-400" />
                    ) : (
                      <Circle size={18} className="text-zinc-700" />
                    )}
                  </div>

                  {/* Step icon */}
                  <StepIcon
                    size={14}
                    className={clsx(
                      'shrink-0',
                      done ? 'text-green-500' : active ? 'text-gold-400' : 'text-zinc-700'
                    )}
                  />

                  {/* Label */}
                  <span
                    className={clsx(
                      'text-sm flex-1',
                      done ? 'text-zinc-500 line-through decoration-zinc-700' : active ? 'text-zinc-100 font-medium' : 'text-zinc-600'
                    )}
                  >
                    {step.label}
                  </span>

                  {done && (
                    <span className="text-xs text-green-500 font-medium">Fatto</span>
                  )}
                </div>
              )
            })}
          </div>

          {/* Progress bar */}
          <div className="w-full bg-zinc-800 rounded-full h-1">
            <div
              className="bg-gold-400 h-1 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <p className="text-xs text-zinc-600 mt-3 text-center">
            La scansione richiede 40–60 secondi · Agenti in parallelo
          </p>
        </div>
      )}

      {/* ── Results ── */}
      {result && !isPending && (
        <div>
          {/* Market Intelligence panels */}
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
          <div className="flex items-start justify-between mb-5 gap-4">
            <div>
              <h2 className="font-display font-semibold text-zinc-100 text-lg">
                <span className="text-gold-400">{filteredListings.length}</span> offerte trovate per{' '}
                <span className="text-gold-400">{result.query.reference}</span>
                {filteredListings.length < result.total_found && (
                  <span className="text-zinc-600 font-normal"> ({result.total_found} totali)</span>
                )}
              </h2>
              <p className="text-xs text-zinc-500 mt-1">
                Completato in {result.duration_seconds.toFixed(1)}s · Agenti:{' '}
                {result.agents_used.join(', ') || 'nessuno'}
              </p>
            </div>

            {result.best_price && (
              <div className="text-right bg-zinc-900 border border-gold-400/25 rounded-xl px-4 py-3 shrink-0">
                <p className="text-xs text-zinc-500 mb-0.5 uppercase tracking-wider">Miglior prezzo</p>
                <p className="font-display font-bold text-2xl text-gold-400">
                  {filteredListings.length > 0
                    ? filteredListings[0].price.toLocaleString('it-IT')
                    : result.best_price.toLocaleString('it-IT')} €
                </p>
              </div>
            )}
          </div>

          {/* Seller search */}
          <div className="relative mb-4">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" />
            <input
              value={filterSeller}
              onChange={e => setFilterSeller(e.target.value)}
              placeholder="Filtra per venditore (es. edwatch, subito, chrono24…)"
              className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-9 pr-4 py-2.5 text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-zinc-600 text-xs"
            />
          </div>

          {/* Filter bar */}
          <div className="flex items-center gap-6 mb-5 flex-wrap">
            {/* Geo filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500">Zona:</span>
              {(['all', 'italy', 'europe'] as const).map(opt => (
                <button
                  key={opt}
                  onClick={() => setFilterGeo(opt)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                    filterGeo === opt
                      ? 'bg-gold-400/20 border-gold-400 text-gold-400'
                      : 'bg-zinc-800 border-zinc-700 text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  {opt === 'all' ? '🌍 Tutto il mondo' : opt === 'italy' ? '🇮🇹 Italia' : '🇪🇺 Europa'}
                </button>
              ))}
            </div>

            {/* Set filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500">Accessori:</span>
              {(['all', 'fullset', 'watchonly'] as const).map(opt => (
                <button
                  key={opt}
                  onClick={() => setFilterSet(opt)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                    filterSet === opt
                      ? 'bg-gold-400/20 border-gold-400 text-gold-400'
                      : 'bg-zinc-800 border-zinc-700 text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  {opt === 'all' ? '⌚ Tutti' : opt === 'fullset' ? '📦 Con scatola/garanzia' : '💎 Solo orologio'}
                </button>
              ))}
            </div>

            {/* Filtered count */}
            <span className="text-xs text-zinc-600 ml-auto">
              {filteredListings.length} di {result.listings.length} risultati
            </span>
          </div>

          {/* Empty state */}
          {filteredListings.length === 0 ? (
            <div className="text-center py-20 bg-zinc-900 border border-zinc-800 rounded-2xl">
              <Search size={40} className="mx-auto mb-4 text-zinc-700" />
              <p className="font-semibold text-zinc-300 mb-2">
                {result.listings.length === 0
                  ? `Nessuna offerta trovata per ${result.query.reference}`
                  : 'Nessun risultato con i filtri selezionati'}
              </p>
              <p className="text-sm text-zinc-600 max-w-xs mx-auto">
                {result.listings.length === 0
                  ? 'Prova senza prezzo massimo o con una referenza diversa'
                  : 'Prova a cambiare zona o filtro accessori'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredListings.map((listing, i) => {
                const isBestDeal =
                  medianForDeal > 0 && listing.price < medianForDeal * 0.90
                return (
                  <ListingCard
                    key={`${listing.source}-${listing.url}-${i}`}
                    listing={listing}
                    isBest={i === 0}
                    isBestDeal={isBestDeal}
                  />
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
