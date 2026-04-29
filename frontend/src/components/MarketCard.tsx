import { TrendingUp, TrendingDown, Minus, Activity, Droplets } from 'lucide-react'
import { clsx } from 'clsx'
import type { MarketStats, InvestmentScore } from '../types'

interface MarketCardProps {
  stats: MarketStats
  investment: InvestmentScore
  trendPct7d?: number   // optional % variazione 7 giorni
}

const SIGNAL_STYLES: Record<InvestmentScore['signal'], string> = {
  buy:   'bg-green-500/20 border-green-500/40 text-green-300',
  hold:  'bg-yellow-500/20 border-yellow-500/40 text-yellow-300',
  avoid: 'bg-red-500/20 border-red-500/40 text-red-300',
}

const SIGNAL_LABELS: Record<InvestmentScore['signal'], string> = {
  buy:   'ACQUISTA',
  hold:  'ATTENDI',
  avoid: 'EVITA',
}

const SIGNAL_BG: Record<InvestmentScore['signal'], string> = {
  buy:   'bg-green-500/10 border-green-500/25',
  hold:  'bg-yellow-500/10 border-yellow-500/25',
  avoid: 'bg-red-500/10 border-red-500/25',
}

const LIQUIDITY_COLORS: Record<InvestmentScore['liquidity'], string> = {
  high:   'text-green-400',
  medium: 'text-yellow-400',
  low:    'text-red-400',
}

const LIQUIDITY_LABELS: Record<InvestmentScore['liquidity'], string> = {
  high:   'Alta',
  medium: 'Media',
  low:    'Bassa',
}

const TREND_MAP = {
  up:     { label: 'In salita', color: 'text-green-400', arrow: '↑' },
  down:   { label: 'In calo',   color: 'text-red-400',   arrow: '↓' },
  stable: { label: 'Stabile',   color: 'text-zinc-400',  arrow: '→' },
}

function fmt(n: number) {
  return n.toLocaleString('it-IT')
}

/** Dots indicator for liquidity (●●●○○ style) */
function LiquidityDots({ level }: { level: InvestmentScore['liquidity'] }) {
  const filled = level === 'high' ? 5 : level === 'medium' ? 3 : 1
  return (
    <span className="inline-flex gap-0.5 items-center">
      {Array.from({ length: 5 }).map((_, i) => (
        <span
          key={i}
          className={clsx(
            'inline-block rounded-full w-2 h-2',
            i < filled
              ? level === 'high'   ? 'bg-green-400'
              : level === 'medium' ? 'bg-yellow-400'
              :                       'bg-red-400'
              : 'bg-zinc-700'
          )}
        />
      ))}
    </span>
  )
}

/** Score bar: filled blocks 0-10 */
function ScoreBar({ score }: { score: number }) {
  const blocks = Math.round(score / 10)
  const color =
    score >= 70 ? 'bg-green-500' :
    score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex gap-0.5 items-center">
      {Array.from({ length: 10 }).map((_, i) => (
        <span
          key={i}
          className={clsx(
            'inline-block rounded-sm h-2 w-4',
            i < blocks ? color : 'bg-zinc-700'
          )}
        />
      ))}
    </div>
  )
}

/** Volatility colored bar */
function VolatilityBar({ pct }: { pct: number }) {
  const color =
    pct < 30 ? 'bg-green-500' :
    pct < 60 ? 'bg-yellow-500' : 'bg-red-500'
  const label =
    pct < 30 ? 'Bassa' :
    pct < 60 ? 'Media' : 'Alta'
  const labelColor =
    pct < 30 ? 'text-green-400' :
    pct < 60 ? 'text-yellow-400' : 'text-red-400'
  return (
    <div className="flex items-center gap-2 flex-1">
      <div className="flex-1 bg-zinc-800 rounded-full h-1.5 max-w-[120px]">
        <div
          className={clsx('h-1.5 rounded-full transition-all', color)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={clsx('text-xs font-medium', labelColor)}>{label}</span>
    </div>
  )
}

export default function MarketCard({ stats, investment, trendPct7d }: MarketCardProps) {
  const volatilityPct = Math.min(100, Math.round(investment.volatility * 100))
  const trend = TREND_MAP[investment.trend]
  const score = investment.investment_score

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-0.5">Analisi di Mercato</p>
          <h3 className="font-display font-bold text-zinc-100 text-lg tracking-tight">
            {stats.reference}
          </h3>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {/* Prezzo Equo — featured */}
        <div className="sm:col-span-2 bg-zinc-800/60 rounded-xl p-4 border border-gold-400/15">
          <p className="text-xs text-zinc-500 mb-1">Prezzo Equo</p>
          <p className="font-display font-bold text-3xl text-gold-400">
            {fmt(stats.fair_price)} €
          </p>
          <p className="text-xs text-zinc-600 mt-1">
            Campione: {stats.sample_size} annunci
          </p>
        </div>

        {/* Prezzo Min */}
        <div className="bg-zinc-800/40 rounded-xl p-4 border border-zinc-700/40">
          <p className="text-xs text-zinc-500 mb-1">Prezzo Min</p>
          <p className="font-semibold text-zinc-100 text-lg">{fmt(stats.min_price)} €</p>
        </div>

        {/* Prezzo Max */}
        <div className="bg-zinc-800/40 rounded-xl p-4 border border-zinc-700/40">
          <p className="text-xs text-zinc-500 mb-1">Prezzo Max</p>
          <p className="font-semibold text-zinc-100 text-lg">{fmt(stats.max_price)} €</p>
        </div>

        {/* P25 */}
        <div className="bg-zinc-800/40 rounded-xl p-4 border border-zinc-700/40">
          <p className="text-xs text-zinc-500 mb-1">P25 — Occasione</p>
          <p className="font-semibold text-green-400 text-base">{fmt(stats.p25)} €</p>
        </div>

        {/* Mediana */}
        <div className="bg-zinc-800/40 rounded-xl p-4 border border-zinc-700/40">
          <p className="text-xs text-zinc-500 mb-1">Mediana</p>
          <p className="font-semibold text-zinc-100 text-base">{fmt(stats.median_price)} €</p>
        </div>

        {/* P75 */}
        <div className="bg-zinc-800/40 rounded-xl p-4 border border-zinc-700/40">
          <p className="text-xs text-zinc-500 mb-1">P75 — Premium</p>
          <p className="font-semibold text-zinc-400 text-base">{fmt(stats.p75)} €</p>
        </div>

        {/* Liquidità */}
        <div className="bg-zinc-800/40 rounded-xl p-4 border border-zinc-700/40">
          <p className="text-xs text-zinc-500 mb-1">Liquidità</p>
          <p className={clsx('font-semibold text-base', LIQUIDITY_COLORS[investment.liquidity])}>
            {LIQUIDITY_LABELS[investment.liquidity]}
          </p>
        </div>
      </div>

      {/* ── Investment panel ── */}
      <div className={clsx(
        'rounded-xl border p-4 space-y-3',
        SIGNAL_BG[investment.signal]
      )}>
        {/* Row 1: Segnale */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-zinc-400 uppercase tracking-widest font-medium">Segnale</span>
          <span className={clsx(
            'inline-flex items-center rounded-full border px-4 py-1 text-sm font-bold tracking-widest',
            SIGNAL_STYLES[investment.signal]
          )}>
            {SIGNAL_LABELS[investment.signal]}
          </span>
        </div>

        {/* Row 2: Indice Investimento */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-400 shrink-0 w-40">Indice Investimento</span>
          <ScoreBar score={score} />
          <span className="font-bold text-gold-400 text-sm shrink-0 w-16 text-right">
            {score.toFixed(0)}/100
          </span>
        </div>

        {/* Row 3: Tendenza */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-400 shrink-0 w-40">Tendenza</span>
          <span className={clsx('text-sm font-semibold flex items-center gap-1', trend.color)}>
            <span className="text-base leading-none">{trend.arrow}</span>
            {trend.label}
            {trendPct7d !== undefined && (
              <span className="text-xs font-normal ml-1 opacity-75">
                ({trendPct7d > 0 ? '+' : ''}{trendPct7d.toFixed(1)}% — 7 giorni)
              </span>
            )}
          </span>
        </div>

        {/* Row 4: Volatilità */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-400 shrink-0 w-40 flex items-center gap-1">
            <Activity size={12} className="text-zinc-500" />
            Volatilità
          </span>
          <VolatilityBar pct={volatilityPct} />
        </div>

        {/* Row 5: Liquidità */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-400 shrink-0 w-40 flex items-center gap-1">
            <Droplets size={12} className="text-zinc-500" />
            Liquidità
          </span>
          <div className="flex items-center gap-2">
            <LiquidityDots level={investment.liquidity} />
            <span className={clsx('text-sm font-medium', LIQUIDITY_COLORS[investment.liquidity])}>
              {LIQUIDITY_LABELS[investment.liquidity]}
            </span>
            <span className="text-xs text-zinc-600">({stats.sample_size} annunci)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
