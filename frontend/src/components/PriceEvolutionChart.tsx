import { useState, useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts'
import { format, parseISO, subYears } from 'date-fns'
import { it } from 'date-fns/locale'
import type { PriceSnapshot } from '../types'

interface PriceEvolutionChartProps {
  history: PriceSnapshot[]
  fairPrice: number
  reference: string
}

type Period = '1A' | '5A' | '10A' | '20A'

const PERIOD_YEARS: Record<Period, number> = {
  '1A': 1,
  '5A': 5,
  '10A': 10,
  '20A': 20,
}

const PERIODS: Period[] = ['1A', '5A', '10A', '20A']

function formatXTick(value: string): string {
  try {
    return format(parseISO(value), 'MM/yyyy', { locale: it })
  } catch {
    return value
  }
}

function fmtEur(value: number): string {
  return `€${value.toLocaleString('it-IT')}`
}

interface TooltipEntry {
  name: string
  value: number
  color: string
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: TooltipEntry[]
  label?: string
}) {
  if (!active || !payload?.length) return null

  let dateLabel = label ?? ''
  try {
    dateLabel = format(parseISO(label ?? ''), 'dd MMM yyyy', { locale: it })
  } catch {
    // keep original
  }

  const labelMap: Record<string, string> = {
    median_price: 'Mediana',
    min_price: 'Min',
    max_price: 'Max',
  }

  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 shadow-xl text-xs space-y-1">
      <p className="text-zinc-400 font-semibold mb-2">Data: {dateLabel}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center justify-between gap-4">
          <span className="text-zinc-400">{labelMap[p.name] ?? p.name}</span>
          <span className="text-zinc-100 font-bold">{p.value.toLocaleString('it-IT')} €</span>
        </div>
      ))}
    </div>
  )
}

export default function PriceEvolutionChart({
  history,
  fairPrice,
  reference,
}: PriceEvolutionChartProps) {
  const [period, setPeriod] = useState<Period>('1A')

  const filtered = useMemo(() => {
    const cutoff = subYears(new Date(), PERIOD_YEARS[period])
    return history
      .filter(s => {
        try {
          return parseISO(s.date) >= cutoff
        } catch {
          return false
        }
      })
      .sort((a, b) => a.date.localeCompare(b.date))
  }, [history, period])

  const hasData = filtered.length > 0
  const isPartial = hasData && filtered.length < 7

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-5 gap-4">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-0.5">Distribuzione Prezzi</p>
          <h3 className="font-semibold text-zinc-100 text-sm">
            Andamento storico — {reference}
          </h3>
        </div>

        {/* Period selector */}
        <div className="flex items-center gap-1 shrink-0 bg-zinc-800 rounded-lg p-1">
          {PERIODS.map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`text-xs px-3 py-1.5 rounded-md font-medium transition-all ${
                period === p
                  ? 'bg-gold-400 text-zinc-900'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Fair price legend */}
      <div className="flex items-center gap-2 text-xs mb-4">
        <span className="w-6 h-0.5 bg-gold-400 inline-block rounded border-dashed border border-gold-400" />
        <span className="text-zinc-500">Prezzo Equo: {fairPrice.toLocaleString('it-IT')} €</span>
      </div>

      {/* Chart or empty state */}
      {!hasData ? (
        <div className="flex items-center justify-center h-48 rounded-xl border border-zinc-800 bg-zinc-800/30">
          <p className="text-sm text-zinc-500 text-center px-6">
            Dati storici non ancora disponibili per questo periodo
          </p>
        </div>
      ) : (
        <>
          {isPartial && (
            <div className="mb-3 text-xs text-zinc-500 flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-yellow-500" />
              Dati parziali — il grafico si arricchirà nel tempo
            </div>
          )}

          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={filtered} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="gradGold" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#D4AF37" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#D4AF37" stopOpacity={0.03} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" vertical={false} />

              <XAxis
                dataKey="date"
                tickFormatter={formatXTick}
                tick={{ fill: '#71717a', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                interval="preserveStartEnd"
              />

              <YAxis
                tick={{ fill: '#71717a', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                width={62}
                tickFormatter={(v: number) =>
                  v >= 1000 ? `€${(v / 1000).toFixed(0)}k` : `€${v}`
                }
              />

              <Tooltip content={<CustomTooltip />} />

              {/* Fair price reference line */}
              <ReferenceLine
                y={fairPrice}
                stroke="#D4AF37"
                strokeWidth={1.5}
                strokeDasharray="5 4"
                label={{
                  value: 'Prezzo Equo',
                  position: 'right',
                  fill: '#D4AF37',
                  fontSize: 9,
                  fontWeight: 600,
                }}
              />

              {/* Min dashed */}
              <Area
                type="monotone"
                dataKey="min_price"
                name="min_price"
                stroke="#71717a"
                strokeWidth={1.5}
                strokeDasharray="4 3"
                fill="transparent"
                dot={false}
                activeDot={{ r: 4 }}
              />

              {/* Median area (gold) */}
              <Area
                type="monotone"
                dataKey="median_price"
                name="median_price"
                stroke="#D4AF37"
                strokeWidth={2}
                fill="url(#gradGold)"
                dot={false}
                activeDot={{ r: 5, stroke: '#D4AF37', strokeWidth: 2, fill: '#18181b' }}
              />

              {/* Max dashed */}
              <Area
                type="monotone"
                dataKey="max_price"
                name="max_price"
                stroke="#52525b"
                strokeWidth={1.5}
                strokeDasharray="4 3"
                fill="transparent"
                dot={false}
                activeDot={{ r: 4 }}
              />
            </AreaChart>
          </ResponsiveContainer>

          {/* Legend */}
          <div className="flex items-center gap-4 mt-3 text-xs text-zinc-500">
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 bg-gold-400 inline-block" />
              Mediana
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-px border-t border-dashed border-zinc-500 inline-block" />
              Min / Max
            </span>
            <span className="ml-auto text-zinc-600">
              {filtered.length} rilevazioni
            </span>
          </div>
        </>
      )}
    </div>
  )
}
