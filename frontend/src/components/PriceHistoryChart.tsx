import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { it } from 'date-fns/locale'
import type { PriceSnapshot } from '../types'

interface PriceHistoryChartProps {
  history: PriceSnapshot[]
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ name: string; value: number; color: string }>
  label?: string
}) {
  if (!active || !payload?.length) return null

  let dateLabel = label ?? ''
  try {
    dateLabel = format(parseISO(label ?? ''), 'dd MMM yyyy', { locale: it })
  } catch {
    // keep original
  }

  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 shadow-xl text-xs space-y-1">
      <p className="text-zinc-400 font-semibold mb-2">{dateLabel}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5" style={{ color: p.color }}>
            <span
              className="w-2 h-2 rounded-full inline-block"
              style={{ background: p.color }}
            />
            {p.name}
          </span>
          <span className="text-zinc-100 font-bold">{p.value.toLocaleString('it-IT')} €</span>
        </div>
      ))}
    </div>
  )
}

function formatXTick(value: string): string {
  try {
    return format(parseISO(value), 'dd/MM', { locale: it })
  } catch {
    return value
  }
}

export default function PriceHistoryChart({ history }: PriceHistoryChartProps) {
  if (!history.length) return null

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
      <div className="mb-5">
        <p className="text-xs text-zinc-500 uppercase tracking-wider mb-0.5">Storico prezzi</p>
        <h3 className="font-semibold text-zinc-100 text-sm">Andamento negli ultimi 30 giorni</h3>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <ComposedChart data={history} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="gradMedian" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#d4a82a" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#d4a82a" stopOpacity={0.02} />
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
            width={56}
            tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '12px' }}
          />

          {/* min_price dashed line */}
          <Line
            type="monotone"
            dataKey="min_price"
            name="Min"
            stroke="#71717a"
            strokeWidth={1.5}
            strokeDasharray="4 3"
            dot={false}
            activeDot={{ r: 4 }}
          />

          {/* median area */}
          <Area
            type="monotone"
            dataKey="median_price"
            name="Mediana"
            stroke="#d4a82a"
            strokeWidth={2}
            fill="url(#gradMedian)"
            dot={false}
            activeDot={{ r: 5, stroke: '#d4a82a', strokeWidth: 2, fill: '#18181b' }}
          />

          {/* max_price dashed line */}
          <Line
            type="monotone"
            dataKey="max_price"
            name="Max"
            stroke="#71717a"
            strokeWidth={1.5}
            strokeDasharray="4 3"
            dot={false}
            activeDot={{ r: 4 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Sample size note */}
      <p className="text-xs text-zinc-600 mt-3">
        Media campioni per giorno:{' '}
        {Math.round(history.reduce((s, h) => s + h.sample_size, 0) / history.length)} annunci
      </p>
    </div>
  )
}
