import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { scanWatch, getPriceHistory, identifyWatchFromImage, getAuctionResults } from '../lib/api'
import type { WatchListing, ScanResult, MarketStats, InvestmentScore, AuctionResult } from '../types'
import MarketCard from '../components/MarketCard'
import PriceEvolutionChart from '../components/PriceEvolutionChart'
import { clsx } from 'clsx'
import { formatDistanceToNow } from 'date-fns'
import { it as itLocale } from 'date-fns/locale'
import { useLang } from '../lib/lang'
import { fmtEur, fmtEurCompact, fmtEurRange } from '../lib/currency'

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

// ---------------------------------------------------------------------------
// Auction Values Panel
// ---------------------------------------------------------------------------

function AuctionValuesPanel({
  reference, results, total, lang,
}: {
  reference: string
  results: AuctionResult[]
  total: number
  lang: string
}) {
  const latest = results[0]
  const record = [...results].sort((a, b) => (b.hammer_price_chf ?? 0) - (a.hammer_price_chf ?? 0))[0]
  const avgHammer = results.reduce((s, r) => s + (r.hammer_price_chf ?? 0), 0) / results.filter(r => r.hammer_price_chf).length || 0

  const fmtChf = (n: number | null | undefined) => fmtEurCompact(n)

  const fmtDate = (iso: string) => {
    try { return new Date(iso).toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { month: 'short', year: 'numeric' }) }
    catch { return iso.slice(0, 7) }
  }

  const houseColor: Record<string, string> = {
    "Phillips":    "text-violet-400",
    "Christie's":  "text-red-400",
    "Sotheby's":   "text-blue-400",
    "Antiquorum":  "text-amber-400",
    "Artcurial":   "text-pink-400",
    "Cambi":       "text-green-400",
    "Bolaffi":     "text-cyan-400",
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 mb-6 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-800 bg-zinc-950/60">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-sm text-yellow-400">gavel</span>
          <span className="font-label-caps text-[10px] uppercase tracking-widest text-zinc-300">
            {lang === 'it' ? 'Ultimo Valore d\'Asta' : 'Auction History'}
          </span>
          <span className="font-mono-data text-[9px] text-zinc-600 ml-1">
            {reference.toUpperCase()} · {total} {lang === 'it' ? 'lotti in DB' : 'lots in DB'}
          </span>
        </div>
        <a
          href={`/aste`}
          className="font-label-caps text-[9px] text-primary hover:text-yellow-300 uppercase tracking-widest flex items-center gap-0.5 transition-colors"
        >
          {lang === 'it' ? 'Vedi tutti' : 'See all'}
          <span className="material-symbols-outlined text-[11px]">arrow_forward</span>
        </a>
      </div>

      <div className="grid grid-cols-12 divide-x divide-zinc-800">
        {/* KPIs colonna sinistra */}
        <div className="col-span-12 lg:col-span-4 p-5 space-y-4">
          {/* Ultimo risultato */}
          <div>
            <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest mb-1">
              {lang === 'it' ? 'Ultima Vendita' : 'Most Recent Sale'}
            </p>
            <p className="font-display-price text-2xl text-zinc-100 leading-none">{fmtChf(latest.hammer_price_chf)}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className={`font-label-caps text-[9px] uppercase ${houseColor[latest.auction_house] ?? 'text-zinc-400'}`}>
                {latest.auction_house}
              </span>
              <span className="text-zinc-600 text-[9px]">·</span>
              <span className="font-mono-data text-[9px] text-zinc-500">{fmtDate(latest.sale_date)}</span>
              {latest.lot_url && (
                <a href={latest.lot_url} target="_blank" rel="noopener noreferrer"
                  className="text-zinc-600 hover:text-yellow-400 transition-colors ml-auto">
                  <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                </a>
              )}
            </div>
            {latest.estimate_low_chf && (
              <p className="font-mono-data text-[10px] text-zinc-600 mt-1">
                Est. {fmtEurRange(latest.estimate_low_chf, latest.estimate_high_chf)}
                {latest.hammer_to_estimate_ratio && latest.hammer_to_estimate_ratio > 1 && (
                  <span className="text-green-400 ml-1">+{((latest.hammer_to_estimate_ratio - 1) * 100).toFixed(0)}% vs est.</span>
                )}
              </p>
            )}
          </div>

          {/* Record assoluto */}
          {record !== latest && (
            <div className="border-t border-zinc-800 pt-4">
              <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest mb-1">
                {lang === 'it' ? 'Record in DB' : 'DB Record'}
              </p>
              <p className="font-display-price text-xl text-primary leading-none">{fmtChf(record.hammer_price_chf)}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`font-label-caps text-[9px] uppercase ${houseColor[record.auction_house] ?? 'text-zinc-400'}`}>
                  {record.auction_house}
                </span>
                <span className="font-mono-data text-[9px] text-zinc-500">· {fmtDate(record.sale_date)}</span>
              </div>
            </div>
          )}

          {/* Media */}
          {avgHammer > 0 && (
            <div className="border-t border-zinc-800 pt-4">
              <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest mb-1">
                {lang === 'it' ? `Media (${results.filter(r => r.hammer_price_chf).length} aste)` : `Avg (${results.filter(r => r.hammer_price_chf).length} sales)`}
              </p>
              <p className="font-mono-data text-sm text-zinc-300">{fmtChf(avgHammer)}</p>
            </div>
          )}
        </div>

        {/* Timeline delle aste — colonna destra */}
        <div className="col-span-12 lg:col-span-8 p-5">
          <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest mb-3">
            {lang === 'it' ? 'Storico Aste' : 'Auction Log'}
          </p>
          <div className="space-y-2">
            {results.slice(0, 5).map((r, i) => {
              const pct = r.hammer_to_estimate_ratio
                ? ((r.hammer_to_estimate_ratio - 1) * 100)
                : null
              return (
                <a
                  key={r.id ?? i}
                  href={r.lot_url || `https://www.google.com/search?q=${encodeURIComponent(`${r.auction_house} ${reference} ${r.sale_date?.slice(0,4)}`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-2.5 bg-zinc-800/30 hover:bg-zinc-800/70 border border-zinc-800 hover:border-zinc-700 transition-colors group rounded"
                >
                  {/* House dot */}
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-zinc-600 group-hover:bg-yellow-400 transition-colors" />

                  {/* House + date */}
                  <div className="w-28 flex-shrink-0">
                    <p className={`font-label-caps text-[9px] uppercase leading-none ${houseColor[r.auction_house] ?? 'text-zinc-400'}`}>
                      {r.auction_house}
                    </p>
                    <p className="font-mono-data text-[9px] text-zinc-600 mt-0.5">{fmtDate(r.sale_date)}</p>
                  </div>

                  {/* Sale name */}
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] text-zinc-500 truncate">
                      {r.sale_name || r.description || reference}
                    </p>
                  </div>

                  {/* Hammer */}
                  <div className="text-right flex-shrink-0">
                    <p className="font-mono-data text-sm text-zinc-100 font-bold leading-none">
                      {fmtChf(r.hammer_price_chf)}
                    </p>
                    {pct !== null && (
                      <p className={`font-mono-data text-[9px] mt-0.5 ${pct > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {pct > 0 ? '+' : ''}{pct.toFixed(0)}%
                      </p>
                    )}
                  </div>

                  <span className="material-symbols-outlined text-[11px] text-zinc-700 group-hover:text-zinc-400 transition-colors flex-shrink-0">
                    open_in_new
                  </span>
                </a>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Listing card
// ---------------------------------------------------------------------------

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

      {/* Image */}
      <div className="w-48 h-48 bg-zinc-950 border border-zinc-800 overflow-hidden flex-shrink-0 flex items-center justify-center grayscale group-hover:grayscale-0 transition-all relative">
        {listing.image_url ? (
          <img
            src={listing.image_url}
            alt={listing.seller}
            className="w-full h-full object-cover"
            onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none'; (e.currentTarget.nextElementSibling as HTMLElement | null)?.style.setProperty('display', 'flex') }}
          />
        ) : null}
        <span
          className="material-symbols-outlined text-5xl text-zinc-700 absolute inset-0 flex items-center justify-center"
          style={{ display: listing.image_url ? 'none' : 'flex' }}
        >watch</span>
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
              {fmtEur(listing.price)}
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

/* ── Submarine Sonar Hunt — responsive side-scroller (slow narrative) ───────
   The sub sits fixed on the left, gently bobbing, already scanning the
   seabed — sonar pings go out and hit nothing. Then the luxury watch drifts
   in SLOWLY from the right. This time a ping catches it, the echo bounces
   back to the sub, and the sub goes into red alarm. One shared 13s period
   keeps watch-travel, detection, echo and alarm in sync. Action lives in the
   vertical centre band so the watch is never cropped on any screen size. */
function SubmarineRadar({ reference, lang }: { reference: string; lang: string }) {
  return (
    <div className="sg-stage">
      <style>{`
        .sg-stage{position:relative;width:100%;height:230px;overflow:hidden;background:#060810}
        @media (max-width:640px){ .sg-stage{height:170px} }
        @keyframes sgBob   { 0%,100%{transform:translate(0,0) rotate(-0.8deg)} 50%{transform:translate(2px,-4px) rotate(0.8deg)} }
        @keyframes sgProp  { from{transform:rotate(0)} to{transform:rotate(360deg)} }
        @keyframes sgBub   { 0%{opacity:.55;transform:translate(0,0) scale(1)} 100%{opacity:0;transform:translate(6px,-66px) scale(.3)} }
        @keyframes sgRay   { 0%,100%{opacity:.3} 50%{opacity:.55} }
        @keyframes sgBed   { from{transform:translateX(0)} to{transform:translateX(-600px)} }
        @keyframes sgLabel { 0%,100%{opacity:.5} 50%{opacity:1} }
        /* continuous sonar ping leaving the nose toward the seabed */
        @keyframes sgPing  { 0%{transform:scale(.3);opacity:0} 18%{opacity:.8} 100%{transform:scale(1.7);opacity:0} }
        @keyframes sgBlip  { 0%,55%{opacity:0} 70%{opacity:.45} 100%{opacity:0} }
        /* watch drifts in slowly from the right, lingers centre, exits left */
        @keyframes sgTravel{ 0%,28%{transform:translateX(710px)} 54%{transform:translateX(312px)} 72%{transform:translateX(300px)} 93%,100%{transform:translateX(-150px)} }
        /* detection visuals ride with the watch, only flash while centred */
        @keyframes sgDetect{ 0%,55%{opacity:0} 60%{opacity:1} 76%{opacity:1} 82%{opacity:0} 100%{opacity:0} }
        @keyframes sgPing2 { 0%,56%{opacity:0;transform:scale(0)} 61%{opacity:1;transform:scale(1.12)} 68%{opacity:1;transform:scale(1)} 80%{opacity:0;transform:scale(1)} 100%{opacity:0} }
        @keyframes sgRing  { 0%,57%{r:6;opacity:0} 59%{opacity:.9} 74%{r:40;opacity:0} 100%{opacity:0} }
        /* echo bouncing back from the watch to the sub */
        @keyframes sgEcho  { 0%,58%{opacity:0;transform:translate(46px,12px)} 61%{opacity:1;transform:translate(46px,12px)} 69%{opacity:.9;transform:translate(0,0)} 72%{opacity:0;transform:translate(0,0)} 100%{opacity:0} }
        /* sub alarm strobe */
        @keyframes sgAlarm { 0%,60%{opacity:0} 63%,69%,75%,81%{opacity:1} 66%,72%,78%,84%{opacity:.2} 88%,100%{opacity:0} }
        @keyframes sgAlarmRing { 0%,61%{transform:scale(.3);opacity:0} 65%{opacity:.75} 80%{transform:scale(1.9);opacity:0} 100%{opacity:0} }
        @media (prefers-reduced-motion: reduce){ .sg-stage *{animation:none !important} }
      `}</style>
      <svg viewBox="0 0 600 240" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="sgWater" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0d1d33"/>
            <stop offset="55%" stopColor="#071426"/>
            <stop offset="100%" stopColor="#030914"/>
          </linearGradient>
          <linearGradient id="sgRayG" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#9fd8ff" stopOpacity="0.15"/>
            <stop offset="100%" stopColor="#9fd8ff" stopOpacity="0"/>
          </linearGradient>
          <radialGradient id="sgDetectG" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#B8975A" stopOpacity="0.55"/>
            <stop offset="65%" stopColor="#B8975A" stopOpacity="0.10"/>
            <stop offset="100%" stopColor="#B8975A" stopOpacity="0"/>
          </radialGradient>
          <filter id="sgGlow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="2.2" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>

        {/* Ocean */}
        <rect width="600" height="240" fill="url(#sgWater)"/>

        {/* God rays */}
        {[90, 250, 410, 540].map((x, i) => (
          <polygon key={i}
            points={`${x},0 ${x + 55},0 ${x + 16},240 ${x - 26},240`}
            fill="url(#sgRayG)"
            style={{ animation: `sgRay ${4 + i}s ease-in-out ${i * 0.5}s infinite` }}/>
        ))}

        {/* Faint grid */}
        {Array.from({ length: 7 }, (_, i) => (
          <line key={i} x1="0" y1={i * 40} x2="600" y2={i * 40} stroke="rgba(184,151,90,0.04)" strokeWidth="1"/>
        ))}

        {/* Scrolling seabed (two seamless copies) */}
        <g style={{ animation: 'sgBed 18s linear infinite' }}>
          {[0, 600].map(off => (
            <g key={off} transform={`translate(${off},0)`}>
              <path d="M0,158 Q100,150 200,156 Q320,164 440,152 Q520,146 600,156 L600,240 L0,240 Z"
                fill="#0a1422" stroke="rgba(184,151,90,0.09)" strokeWidth="1"/>
              <path d="M70,156 q7,-18 14,0 z" fill="#0e1c2e"/>
              <path d="M96,157 q5,-24 10,0 q5,-14 9,0 z" fill="#0e1c2e"/>
              <path d="M470,152 q8,-20 16,0 z" fill="#0e1c2e"/>
              <circle cx="250" cy="180" r="2" fill="rgba(184,151,90,0.15)"/>
              <circle cx="540" cy="186" r="1.5" fill="rgba(184,151,90,0.12)"/>
            </g>
          ))}
        </g>

        {/* empty sonar blip on the seabed (a few pings that hit nothing) */}
        <circle cx="305" cy="150" r="3" fill="none" stroke="rgba(184,151,90,0.5)" strokeWidth="1.5"
          style={{ animation: 'sgBlip 1.65s ease-out infinite' }}/>

        {/* ── Watch drifting in slowly from the right ── */}
        <g style={{ animation: 'sgTravel 13s cubic-bezier(0.45,0,0.55,1) infinite' }}>
          <g transform="translate(0,130)">
            {/* detection halo + shock ring (flash only while centred) */}
            <circle cx="0" cy="0" r="38" fill="url(#sgDetectG)"
              style={{ animation: 'sgDetect 13s linear infinite' }}/>
            <circle cx="0" cy="0" r="6" fill="none" stroke="#B8975A" strokeWidth="2"
              style={{ animation: 'sgRing 13s linear infinite' }}/>
            {/* shadow */}
            <ellipse cx="0" cy="24" rx="24" ry="4.5" fill="rgba(0,0,0,0.35)"/>
            {/* strap */}
            <path d="M -8,-18 L 8,-18 L 6,-28 L -6,-28 Z" fill="#0e1c2e" stroke="#B8975A" strokeWidth="1.3"/>
            <path d="M -8,18 L 8,18 L 6,28 L -6,28 Z"     fill="#0e1c2e" stroke="#B8975A" strokeWidth="1.3"/>
            {/* crown */}
            <rect x="18" y="-3" width="6" height="6" rx="1" fill="#0c1a30" stroke="#B8975A" strokeWidth="1.1"/>
            {/* case */}
            <circle cx="0" cy="0" r="19" fill="#0c1a30" stroke="#B8975A" strokeWidth="2.8"/>
            <circle cx="0" cy="0" r="13.5" fill="#081223" stroke="rgba(184,151,90,0.4)" strokeWidth="1"/>
            {/* ticks */}
            {Array.from({ length: 12 }, (_, i) => {
              const a = (i * 30) * Math.PI / 180
              return <line key={i}
                x1={Math.sin(a) * 11.5} y1={-Math.cos(a) * 11.5}
                x2={Math.sin(a) * 13.5} y2={-Math.cos(a) * 13.5}
                stroke="rgba(184,151,90,0.5)" strokeWidth="1"/>
            })}
            {/* hands */}
            <line x1="0" y1="0" x2="0" y2="-8" stroke="#e8e2d4" strokeWidth="1.5" strokeLinecap="round"/>
            <line x1="0" y1="0" x2="7" y2="3" stroke="#B8975A" strokeWidth="1.3" strokeLinecap="round"/>
            <circle cx="0" cy="0" r="1.5" fill="#B8975A"/>
            {/* reticle brackets */}
            <g stroke="#4EB87A" strokeWidth="2" fill="none" style={{ animation: 'sgDetect 13s linear infinite' }}>
              <path d="M -30,-22 L -30,-30 L -22,-30"/>
              <path d="M 30,-22 L 30,-30 L 22,-30"/>
              <path d="M -30,22 L -30,30 L -22,30"/>
              <path d="M 30,22 L 30,30 L 22,30"/>
            </g>
            {/* comic PING (nudged clear of the dial) */}
            <g transform="translate(38,-42)" style={{ animation: 'sgPing2 13s linear infinite', transformOrigin: '38px -42px' }}>
              <polygon points="0,-13 4,-4 13,-5 6,1 9,11 0,5 -9,11 -6,1 -13,-5 -4,-4"
                fill="#B8975A" stroke="#e8e2d4" strokeWidth="1"/>
              <text x="0" y="3" textAnchor="middle"
                fontFamily='"Space Grotesk", system-ui, sans-serif' fontSize="7" fontWeight="700"
                fill="#081223">PING</text>
            </g>
          </g>
        </g>

        {/* ── Echo bouncing back from the watch to the sub ── */}
        <g transform="translate(259,118)" style={{ animation: 'sgEcho 13s linear infinite' }}>
          <circle cx="0" cy="0" r="3" fill="#4EB87A" filter="url(#sgGlow)"/>
          <path d="M 6,-8 A 10,10 0 0 1 6,8" fill="none" stroke="#4EB87A" strokeWidth="2" opacity="0.7"/>
        </g>

        {/* ── Submarine — fixed on the left, scanning the seabed ── */}
        <g transform="translate(175,118)">
          {/* continuous sonar pings toward the seabed (down-right) */}
          <g transform="translate(80,2) rotate(14)">
            {[0, 0.55, 1.1].map((d, i) => (
              <path key={i} d="M 0,-22 A 22,22 0 0 1 0,22" fill="none"
                stroke="#B8975A" strokeWidth="2.2" strokeLinecap="round"
                style={{ transformOrigin: '0px 0px', animation: `sgPing 1.65s ease-out ${d}s infinite` }}/>
            ))}
          </g>

          {/* alarm rings around the sub (fire on contact) */}
          <circle cx="0" cy="-6" r="40" fill="none" stroke="#E05A5A" strokeWidth="2.5"
            style={{ transformOrigin: '0px -6px', animation: 'sgAlarmRing 13s ease-out infinite' }}/>

          <g style={{ animation: 'sgBob 4.5s ease-in-out infinite', transformOrigin: '0px 0px' }}>
            {/* propeller */}
            <g style={{ transformOrigin: '-78px 0px' }}>
              <g style={{ animation: 'sgProp 0.9s linear infinite', transformOrigin: '-78px 0px' }}>
                <ellipse cx="-78" cy="-13" rx="4" ry="13" fill="#B8975A" opacity="0.75" transform="rotate(-18 -78 0)"/>
                <ellipse cx="-78" cy="13"  rx="4" ry="13" fill="#B8975A" opacity="0.75" transform="rotate(18 -78 0)"/>
              </g>
              <circle cx="-78" cy="0" r="3.5" fill="#0d1e35" stroke="#B8975A" strokeWidth="1.4"/>
            </g>
            <line x1="-78" y1="0" x2="-60" y2="0" stroke="#B8975A" strokeWidth="2"/>
            {/* tail fins */}
            <polygon points="-60,9 -76,26 -60,2"  fill="#0d1e35" stroke="#B8975A" strokeWidth="1.3"/>
            <polygon points="-60,-9 -76,-26 -60,-2" fill="#0d1e35" stroke="#B8975A" strokeWidth="1.3"/>
            {/* hull */}
            <path d="M -64,0 Q -64,-26 -40,-26 L 54,-26 Q 80,-26 80,0 Q 80,26 54,26 L -40,26 Q -64,26 -64,0 Z"
              fill="#0c1a30" stroke="#B8975A" strokeWidth="2.8"/>
            <path d="M -38,-21 Q 26,-26 76,-10" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="2.6" strokeLinecap="round"/>
            {/* conning tower (compact) */}
            <rect x="-14" y="-44" width="30" height="22" rx="6" fill="#0d1e35" stroke="#B8975A" strokeWidth="2.2"/>
            <line x1="2" y1="-44" x2="2" y2="-54" stroke="#B8975A" strokeWidth="2.2"/>
            <line x1="2" y1="-54" x2="14" y2="-54" stroke="#B8975A" strokeWidth="2.2"/>
            {/* scanning light (green) */}
            <circle cx="14" cy="-54" r="3" fill="#4EB87A" filter="url(#sgGlow)"/>
            {/* alarm light (red, strobes on contact) — overlaps the green one */}
            <circle cx="14" cy="-54" r="3.4" fill="#E05A5A" filter="url(#sgGlow)"
              style={{ animation: 'sgAlarm 13s linear infinite' }}/>
            {/* portholes */}
            {[-34, -8, 16].map((x, i) => (
              <g key={i}>
                <circle cx={x} cy="2" r="8" fill="#081223" stroke="#B8975A" strokeWidth="1.8"/>
                <circle cx={x} cy="2" r="4.8" fill="rgba(255,225,150,0.22)"/>
                {/* red wash inside portholes during alarm */}
                <circle cx={x} cy="2" r="4.8" fill="#E05A5A" opacity="0"
                  style={{ animation: 'sgAlarm 13s linear infinite' }}/>
                <circle cx={x - 2} cy={-0.4} r="1.6" fill="rgba(255,255,255,0.18)"/>
              </g>
            ))}
            {/* nose emitter */}
            <ellipse cx="80" cy="2" rx="8" ry="14" fill="#0c1a30" stroke="#B8975A" strokeWidth="1.8"/>
            {/* bubbles */}
            {[{ x: 5, d: '0s', r: 3 }, { x: 11, d: '0.9s', r: 2.2 }, { x: 1, d: '1.7s', r: 3.5 }].map((b, i) => (
              <circle key={i} cx={b.x} cy={-52} r={b.r}
                fill="none" stroke="rgba(159,216,255,0.5)" strokeWidth="1"
                style={{ animation: `sgBub 3s ease-out ${b.d} infinite` }}/>
            ))}
          </g>

          {/* alarm badge "⚠ CONTATTO" appears on contact, upper-right of sub */}
          <g style={{ animation: 'sgAlarm 13s linear infinite' }}>
            <text x="26" y="-30" fontFamily='"IBM Plex Mono", monospace' fontSize="10" fontWeight="700"
              fill="#E05A5A" letterSpacing="1.5">⚠ CONTATTO</text>
          </g>
        </g>

        {/* HUD */}
        <text x="18" y="22" fontFamily='"IBM Plex Mono", monospace' fontSize="9"
          fill="#4EB87A" letterSpacing="1.5" style={{ animation: 'sgLabel 1.8s ease-in-out infinite' }}>
          ● SONAR ATTIVO
        </text>
        <text x="300" y="232" textAnchor="middle" fontFamily='"IBM Plex Mono", monospace' fontSize="9.5"
          fill="#B8975A" letterSpacing="3">
          {(reference.toUpperCase() || '—')} · {lang === 'it' ? 'SCANDAGLIO IN CORSO' : 'SCANNING THE DEEP'}
        </text>
      </svg>
    </div>
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
  const { t, lang } = useLang()
  const [reference, setReference] = useState(params.get('ref') || '')
  const [maxPrice, setMaxPrice] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [scanStep, setScanStep] = useState(0)
  const [scanTimer, setScanTimer] = useState(0)
  const scanTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [scanEncyclopedia, setScanEncyclopedia] = useState<import('../types').EncyclopediaWatch | null>(null)
  const [scanEncyLoading, setScanEncyLoading] = useState(false)
  const [filterGeo, setFilterGeo] = useState<'all'|'italy'|'europe'>('all')
  const [filterSet, setFilterSet] = useState<'all'|'fullset'|'watchonly'>('all')
  const [filterSeller, setFilterSeller] = useState('')
  const [filterPriceMin, setFilterPriceMin] = useState('')
  const [filterPriceMax, setFilterPriceMax] = useState('')
  const [filterSources, setFilterSources] = useState<Set<string>>(new Set())
  const scanStepRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [showRelated, setShowRelated] = useState(false)
  const [identifying, setIdentifying] = useState(false)
  const [identifyResult, setIdentifyResult] = useState<{brand:string|null;model:string|null;reference:string|null;confidence:number;notes:string|null}|null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: scanWatch,
    onSuccess: (data) => {
      if (scanStepRef.current) clearTimeout(scanStepRef.current)
      if (scanTimerRef.current) { clearInterval(scanTimerRef.current); scanTimerRef.current = null }
      setScanStep(SCAN_STEPS.length)
      setResult(data)
      setError(null)
    },
    onError: (err: any) => {
      if (scanStepRef.current) clearTimeout(scanStepRef.current)
      if (scanTimerRef.current) { clearInterval(scanTimerRef.current); scanTimerRef.current = null }
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
    setError(null); setResult(null); setScanStep(0); setScanTimer(0); setScanEncyclopedia(null)
    setFilterGeo('all'); setFilterSet('all'); setFilterSeller('')
    setFilterPriceMin(''); setFilterPriceMax(''); setFilterSources(new Set())

    // Timer
    if (scanTimerRef.current) clearInterval(scanTimerRef.current)
    scanTimerRef.current = setInterval(() => setScanTimer(s => s + 1), 1000)

    // Fetch enciclopedia in parallelo
    setScanEncyLoading(true)
    fetch(`/api/encyclopedia/reference/${encodeURIComponent(target.toUpperCase())}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { setScanEncyclopedia(data); setScanEncyLoading(false) })
      .catch(() => setScanEncyLoading(false))

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
    if (ref) handleScan(ref)
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const { data: auctionData } = useQuery({
    queryKey: ['auction-results-search', result?.query.reference],
    queryFn: () => getAuctionResults(result!.query.reference, { limit: 5 }),
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
        <div className="space-y-4">

          {/* Submarine radar animation */}
          <div className="border border-zinc-800">
            <SubmarineRadar reference={reference} lang={lang} />
            {/* copy */}
            <div className="px-5 py-3 bg-zinc-900 border-t border-zinc-800">
              <p className="text-yellow-400 font-bold uppercase tracking-[0.18em] text-[10px] mb-1">
                SONAR ACTIVE · SCANNING DEPTH
              </p>
              <p style={{ fontFamily: '"Space Grotesk", system-ui, sans-serif' }} className="font-semibold text-zinc-300 text-sm leading-snug">
                {lang === 'it'
                  ? 'Scandagliamo ogni angolo del web fino agli abissi per trovare il prezzo migliore.'
                  : 'We dive to the deepest corners of the web to surface the best price.'}
              </p>
            </div>
          </div>

          {/* Header: timer + barra progresso */}
          <div className="bg-zinc-900 border border-zinc-800 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-xl text-yellow-400 animate-spin">autorenew</span>
                <div>
                  <p className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-sm">
                    {t.scanningFor} <span className="text-yellow-400">{reference.toUpperCase()}</span>
                  </p>
                  <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-0.5">
                    {SCAN_STEPS[Math.min(scanStep, SCAN_STEPS.length - 1)]?.label}
                  </p>
                </div>
              </div>
              {/* Contatore secondi */}
              <div className="text-right">
                <span className="font-mono text-3xl font-bold tabular-nums text-zinc-100 leading-none">
                  {String(Math.floor(scanTimer / 60)).padStart(2, '0')}:{String(scanTimer % 60).padStart(2, '0')}
                </span>
                <p className="text-[9px] text-zinc-600 uppercase tracking-widest mt-1">
                  {lang === 'it' ? 'tempo trascorso' : 'elapsed'}
                </p>
              </div>
            </div>
            {/* Barra progresso */}
            <div className="w-full bg-zinc-800 h-0.5 rounded-full overflow-hidden">
              <div
                className="bg-yellow-400 h-0.5 rounded-full transition-all duration-700"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            {/* Step pill */}
            <div className="flex gap-1.5 mt-3">
              {SCAN_STEPS.map((_, i) => (
                <div key={i} className={clsx(
                  'h-1 flex-1 rounded-full transition-all duration-500',
                  i < scanStep ? 'bg-green-500' : i === scanStep ? 'bg-yellow-400' : 'bg-zinc-800'
                )} />
              ))}
            </div>
          </div>

          {/* Scheda enciclopedia */}
          <div className="bg-zinc-900 border border-zinc-800 overflow-hidden">
            {scanEncyLoading && !scanEncyclopedia ? (
              <div className="p-6 animate-pulse space-y-3">
                <div className="h-3 bg-zinc-800 rounded w-1/3" />
                <div className="h-5 bg-zinc-800 rounded w-2/3" />
                <div className="h-3 bg-zinc-800 rounded w-full" />
                <div className="h-3 bg-zinc-800 rounded w-5/6" />
                <div className="h-3 bg-zinc-800 rounded w-4/6" />
              </div>
            ) : scanEncyclopedia ? (
              <div className="flex gap-0 divide-x divide-zinc-800">
                {/* Colonna sinistra: identità */}
                <div className="p-6 flex-1 min-w-0 space-y-4">
                  <div>
                    <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest mb-1">
                      {scanEncyclopedia.brand}
                    </p>
                    <h2 className="font-['Space_Grotesk'] font-bold text-xl text-zinc-100 leading-tight">
                      {scanEncyclopedia.model}
                    </h2>
                    <p className="font-mono-data text-xs text-yellow-400 mt-0.5">{scanEncyclopedia.reference}</p>
                  </div>

                  {/* Periodo produzione */}
                  {(scanEncyclopedia.year_introduced || scanEncyclopedia.year_discontinued) && (
                    <div className="flex items-center gap-6">
                      {scanEncyclopedia.year_introduced && (
                        <div>
                          <p className="font-label-caps text-[9px] text-zinc-600 uppercase">{lang === 'it' ? 'Anno lancio' : 'Introduced'}</p>
                          <p className="font-mono-data text-lg text-zinc-100 font-bold">{scanEncyclopedia.year_introduced}</p>
                        </div>
                      )}
                      {scanEncyclopedia.year_discontinued ? (
                        <div>
                          <p className="font-label-caps text-[9px] text-zinc-600 uppercase">{lang === 'it' ? 'Fine produzione' : 'Discontinued'}</p>
                          <p className="font-mono-data text-lg text-red-400 font-bold">{scanEncyclopedia.year_discontinued}</p>
                        </div>
                      ) : (
                        <div>
                          <p className="font-label-caps text-[9px] text-zinc-600 uppercase">{lang === 'it' ? 'Stato' : 'Status'}</p>
                          <p className="font-mono-data text-sm text-green-400 font-bold">{lang === 'it' ? 'In produzione' : 'In production'}</p>
                        </div>
                      )}
                      {scanEncyclopedia.is_limited_edition && (
                        <div className="px-2 py-0.5 bg-amber-900/40 border border-amber-700/40 text-amber-400 text-[9px] font-bold uppercase tracking-widest self-center">
                          {lang === 'it' ? 'Edizione Limitata' : 'Limited Edition'}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Descrizione */}
                  {scanEncyclopedia.description && (
                    <p className="text-zinc-400 text-sm leading-relaxed border-l-2 border-yellow-400/30 pl-3">
                      {scanEncyclopedia.description}
                    </p>
                  )}

                  {/* Storie / curiosità */}
                  {scanEncyclopedia.stories && scanEncyclopedia.stories.length > 0 && (
                    <div className="space-y-2">
                      {scanEncyclopedia.stories.slice(0, 2).map((s, i) => (
                        <div key={i} className="bg-zinc-800/50 p-3 border-l border-yellow-400/20">
                          <p className="font-label-caps text-[9px] text-yellow-400/70 uppercase tracking-widest mb-1">{s.category || (lang === 'it' ? 'Storia' : 'History')}</p>
                          <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">{s.content}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Colonna destra: specifiche tecniche + prezzi */}
                <div className="p-6 w-64 flex-shrink-0 space-y-4">
                  {/* Prezzi */}
                  {(scanEncyclopedia.retail_price_eur || scanEncyclopedia.avg_market_price_eur) && (
                    <div className="space-y-2">
                      <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest">{lang === 'it' ? 'Prezzi di riferimento' : 'Reference prices'}</p>
                      {scanEncyclopedia.retail_price_eur && (
                        <div className="flex justify-between items-baseline">
                          <span className="text-xs text-zinc-500">{lang === 'it' ? 'Retail' : 'Retail'}</span>
                          <span className="font-mono-data text-sm text-zinc-300">
                            {scanEncyclopedia.retail_price_eur.toLocaleString('it-IT')} €
                          </span>
                        </div>
                      )}
                      {scanEncyclopedia.avg_market_price_eur && (
                        <div className="flex justify-between items-baseline">
                          <span className="text-xs text-zinc-500">{lang === 'it' ? 'Mercato medio' : 'Avg market'}</span>
                          <span className="font-mono-data text-sm text-yellow-400 font-bold">
                            {scanEncyclopedia.avg_market_price_eur.toLocaleString('it-IT')} €
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Cassa */}
                  {(scanEncyclopedia.case_material || scanEncyclopedia.case_diameter_mm) && (
                    <div className="space-y-1.5">
                      <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest">{lang === 'it' ? 'Cassa' : 'Case'}</p>
                      {scanEncyclopedia.case_material && (
                        <div className="flex justify-between">
                          <span className="text-xs text-zinc-500">{lang === 'it' ? 'Materiale' : 'Material'}</span>
                          <span className="text-xs text-zinc-300">{scanEncyclopedia.case_material}</span>
                        </div>
                      )}
                      {scanEncyclopedia.case_diameter_mm && (
                        <div className="flex justify-between">
                          <span className="text-xs text-zinc-500">{lang === 'it' ? 'Diametro' : 'Diameter'}</span>
                          <span className="font-mono-data text-xs text-zinc-300">{scanEncyclopedia.case_diameter_mm} mm</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Quadrante */}
                  {scanEncyclopedia.dial_color && (
                    <div className="space-y-1.5">
                      <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest">{lang === 'it' ? 'Quadrante' : 'Dial'}</p>
                      <div className="flex justify-between">
                        <span className="text-xs text-zinc-500">{lang === 'it' ? 'Colore' : 'Color'}</span>
                        <span className="text-xs text-zinc-300">{scanEncyclopedia.dial_color}</span>
                      </div>
                    </div>
                  )}

                  {/* Movimento */}
                  {(scanEncyclopedia.movement_type || scanEncyclopedia.movement_caliber) && (
                    <div className="space-y-1.5">
                      <p className="font-label-caps text-[9px] text-zinc-500 uppercase tracking-widest">{lang === 'it' ? 'Movimento' : 'Movement'}</p>
                      {scanEncyclopedia.movement_type && (
                        <div className="flex justify-between">
                          <span className="text-xs text-zinc-500">{lang === 'it' ? 'Tipo' : 'Type'}</span>
                          <span className="text-xs text-zinc-300">{scanEncyclopedia.movement_type}</span>
                        </div>
                      )}
                      {scanEncyclopedia.movement_caliber && (
                        <div className="flex justify-between">
                          <span className="text-xs text-zinc-500">Calibro</span>
                          <span className="font-mono-data text-xs text-zinc-300">{scanEncyclopedia.movement_caliber}</span>
                        </div>
                      )}
                      {scanEncyclopedia.power_reserve_h && (
                        <div className="flex justify-between">
                          <span className="text-xs text-zinc-500">{lang === 'it' ? 'Riserva' : 'Reserve'}</span>
                          <span className="font-mono-data text-xs text-zinc-300">{scanEncyclopedia.power_reserve_h}h</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              /* Nessun dato enciclopedia */
              <div className="p-6 flex items-center gap-4">
                <span className="material-symbols-outlined text-4xl text-zinc-700">watch</span>
                <div>
                  <p className="font-['Space_Grotesk'] font-semibold text-zinc-300 text-sm mb-0.5">
                    {reference.toUpperCase()}
                  </p>
                  <p className="text-xs text-zinc-600">
                    {lang === 'it'
                      ? 'Referenza non ancora in enciclopedia — i risultati di mercato sono in arrivo...'
                      : 'Reference not in encyclopedia yet — market results incoming...'}
                  </p>
                </div>
              </div>
            )}
          </div>
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

          {/* ── Auction Values Panel ── */}
          {auctionData && auctionData.results.length > 0 && (
            <AuctionValuesPanel
              reference={result.query.reference}
              results={auctionData.results}
              total={auctionData.total}
              lang={lang}
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

          {/* Related Listings — collapsible */}
          {result.related_listings && result.related_listings.length > 0 && (
            <div className="mt-6 border border-zinc-800 rounded-none bg-zinc-950">
              <button
                onClick={() => setShowRelated(v => !v)}
                className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-zinc-900 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-zinc-500">blur_on</span>
                  <div>
                    <span className="font-['Space_Grotesk'] font-semibold text-zinc-300 text-sm">
                      {t.relatedListingsTitle}
                    </span>
                    <span className="ml-2 text-xs bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded-full">
                      {result.related_listings.length}
                    </span>
                  </div>
                  <span className="text-xs text-zinc-600 ml-1">{t.relatedListingsSub}</span>
                </div>
                <span className="material-symbols-outlined text-zinc-600 text-base">
                  {showRelated ? 'expand_less' : 'expand_more'}
                </span>
              </button>

              {showRelated && (
                <div className="px-6 pb-6 space-y-4">
                  {result.related_listings.map((listing, i) => (
                    <div key={`rel-${listing.source}-${listing.url}-${i}`} className="relative">
                      <div className="absolute top-3 right-3 z-10 flex items-center gap-1 bg-amber-900/60 border border-amber-700/50 px-2 py-0.5 rounded text-[10px] font-bold tracking-widest text-amber-400 uppercase">
                        <span className="material-symbols-outlined text-[11px]">blur_on</span>
                        {lang === 'it' ? 'CORRELATO' : 'RELATED'}
                      </div>
                      <ListingCard
                        listing={listing}
                        isBest={false}
                        isBestDeal={false}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
