import { clsx } from 'clsx'
import type { MarketStats, InvestmentScore } from '../types'

interface MarketCardProps {
  stats: MarketStats
  investment: InvestmentScore
  trendPct7d?: number
}

const SIGNAL_STYLES: Record<InvestmentScore['signal'], string> = {
  buy:   'bg-green-500/10 border-green-500/30 text-green-400',
  hold:  'bg-yellow-400/10 border-yellow-400/30 text-yellow-400',
  avoid: 'bg-red-500/10 border-red-500/30 text-red-400',
}

const SIGNAL_LABELS: Record<InvestmentScore['signal'], string> = {
  buy:   'ACQUISTA',
  hold:  'ATTENDI',
  avoid: 'EVITA',
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

function fmt(n: number) { return n.toLocaleString('it-IT') }

function LiquidityDots({ level }: { level: InvestmentScore['liquidity'] }) {
  const filled = level === 'high' ? 5 : level === 'medium' ? 3 : 1
  return (
    <span className="inline-flex gap-1 items-center">
      {Array.from({ length: 5 }).map((_, i) => (
        <span
          key={i}
          className={clsx(
            'inline-block rounded-full w-2.5 h-2.5',
            i < filled
              ? level === 'high'   ? 'bg-green-400'
              : level === 'medium' ? 'bg-yellow-400'
              :                      'bg-red-400'
              : 'bg-zinc-800'
          )}
          style={i < filled ? { boxShadow: '0 0 6px rgba(242,195,69,0.4)' } : undefined}
        />
      ))}
    </span>
  )
}

function ScoreBar({ score }: { score: number }) {
  const blocks = Math.round(score / 10)
  const color =
    score >= 70 ? 'bg-green-500' :
    score >= 40 ? 'bg-yellow-400' : 'bg-red-500'
  return (
    <div className="flex gap-0.5 items-center">
      {Array.from({ length: 10 }).map((_, i) => (
        <span key={i} className={clsx('inline-block h-2 w-4', i < blocks ? color : 'bg-zinc-700')} />
      ))}
    </div>
  )
}

function VolatilityBar({ pct }: { pct: number }) {
  const color = pct < 30 ? 'bg-green-500' : pct < 60 ? 'bg-yellow-400' : 'bg-red-500'
  const label = pct < 30 ? 'Bassa' : pct < 60 ? 'Media' : 'Alta'
  const labelColor = pct < 30 ? 'text-green-400' : pct < 60 ? 'text-yellow-400' : 'text-red-400'
  return (
    <div className="flex items-center gap-2 flex-1">
      <div className="flex-1 bg-zinc-800 h-1.5 max-w-[120px]">
        <div className={clsx('h-1.5 transition-all', color)} style={{ width: `${pct}%` }} />
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
    <div className="bg-zinc-900 border border-zinc-800 p-[24px] mb-[12px]">

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-1">Analisi di Mercato</p>
          <h3 className="font-h2 text-h2 text-zinc-100">{stats.reference}</h3>
        </div>
        <span className={clsx('border px-4 py-1 text-sm font-bold tracking-widest rounded', SIGNAL_STYLES[investment.signal])}>
          {SIGNAL_LABELS[investment.signal]}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-[12px] mb-[12px]">

        {/* Prezzo Equo — featured */}
        <div className="sm:col-span-2 bg-zinc-800/60 p-[24px] border border-yellow-400/20">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">Prezzo Equo</p>
          <p className="font-display-price text-display-price text-yellow-400 leading-none">
            {fmt(stats.fair_price)} €
          </p>
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-2">
            Campione: {stats.sample_size} annunci
          </p>
        </div>

        {/* Prezzo Min */}
        <div className="bg-zinc-800/40 p-[24px] border border-zinc-700/40">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">Prezzo Min</p>
          <p className="font-h2 text-xl text-zinc-100">{fmt(stats.min_price)} €</p>
        </div>

        {/* Prezzo Max */}
        <div className="bg-zinc-800/40 p-[24px] border border-zinc-700/40">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">Prezzo Max</p>
          <p className="font-h2 text-xl text-zinc-100">{fmt(stats.max_price)} €</p>
        </div>

        {/* P25 */}
        <div className="bg-zinc-800/40 p-[24px] border border-zinc-700/40">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">P25 — Occasione</p>
          <p className="font-mono-data text-mono-data text-green-400">{fmt(stats.p25)} €</p>
        </div>

        {/* Mediana */}
        <div className="bg-zinc-800/40 p-[24px] border border-zinc-700/40">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">Mediana</p>
          <p className="font-mono-data text-mono-data text-zinc-100">{fmt(stats.median_price)} €</p>
        </div>

        {/* P75 */}
        <div className="bg-zinc-800/40 p-[24px] border border-zinc-700/40">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">P75 — Premium</p>
          <p className="font-mono-data text-mono-data text-zinc-400">{fmt(stats.p75)} €</p>
        </div>

        {/* Liquidità */}
        <div className="bg-zinc-800/40 p-[24px] border border-zinc-700/40">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-2">Liquidità</p>
          <p className={clsx('font-mono-data text-mono-data', LIQUIDITY_COLORS[investment.liquidity])}>
            {LIQUIDITY_LABELS[investment.liquidity]}
          </p>
        </div>
      </div>

      {/* Investment panel */}
      <div className="bg-zinc-800/30 border border-zinc-700/40 p-[24px] space-y-4">

        <div className="flex items-center justify-between">
          <span className="font-label-caps text-label-caps text-zinc-400 uppercase">Segnale</span>
          <span className={clsx('border px-4 py-1 text-xs font-bold tracking-widest rounded', SIGNAL_STYLES[investment.signal])}>
            {SIGNAL_LABELS[investment.signal]}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="font-label-caps text-label-caps text-zinc-400 uppercase w-44">Indice Investimento</span>
          <ScoreBar score={score} />
          <span className="font-mono-data text-mono-data text-yellow-400 w-16 text-right">{score.toFixed(0)}/100</span>
        </div>

        <div className="flex items-center gap-3">
          <span className="font-label-caps text-label-caps text-zinc-400 uppercase w-44">Tendenza</span>
          <span className={clsx('font-mono-data text-sm flex items-center gap-1', trend.color)}>
            {trend.arrow} {trend.label}
            {trendPct7d !== undefined && (
              <span className="text-xs opacity-75 ml-1">({trendPct7d > 0 ? '+' : ''}{trendPct7d.toFixed(1)}%)</span>
            )}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="font-label-caps text-label-caps text-zinc-400 uppercase w-44 flex items-center gap-1">
            <span className="material-symbols-outlined text-sm leading-none text-zinc-500">show_chart</span>
            Volatilità
          </span>
          <VolatilityBar pct={volatilityPct} />
        </div>

        <div className="flex items-center gap-3">
          <span className="font-label-caps text-label-caps text-zinc-400 uppercase w-44 flex items-center gap-1">
            <span className="material-symbols-outlined text-sm leading-none text-zinc-500">water_drop</span>
            Liquidità
          </span>
          <div className="flex items-center gap-2">
            <LiquidityDots level={investment.liquidity} />
            <span className={clsx('font-mono-data text-sm', LIQUIDITY_COLORS[investment.liquidity])}>
              {LIQUIDITY_LABELS[investment.liquidity]}
            </span>
            <span className="text-[10px] text-zinc-500">({stats.sample_size} annunci)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
