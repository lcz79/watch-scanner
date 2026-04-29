import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { PriceDistribution } from '../types'

interface PriceChartProps {
  distribution: PriceDistribution
  fairPrice: number
}

interface TooltipPayload {
  payload?: { range: string; count: number; percentage: number }
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 shadow-xl text-xs">
      <p className="text-zinc-300 font-semibold mb-1">{d.range}</p>
      <p className="text-zinc-400">
        Annunci: <span className="text-zinc-100 font-bold">{d.count}</span>
      </p>
      <p className="text-zinc-400">
        Frequenza: <span className="text-zinc-100 font-bold">{d.percentage.toFixed(1)}%</span>
      </p>
    </div>
  )
}

function findFairBinRange(bins: PriceDistribution['bins'], fairPrice: number): string {
  if (!bins.length) return ''
  const sorted = [...bins].sort((a, b) => {
    const aVal = parseFloat(a.range.split('–')[0].replace(/[^\d]/g, ''))
    const bVal = parseFloat(b.range.split('–')[0].replace(/[^\d]/g, ''))
    return Math.abs(aVal - fairPrice) - Math.abs(bVal - fairPrice)
  })
  return sorted[0]?.range ?? ''
}

export default function PriceChart({ distribution, fairPrice }: PriceChartProps) {
  const { bins } = distribution
  const fairBinRange = findFairBinRange(bins, fairPrice)

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-0.5">Distribuzione prezzi</p>
          <h3 className="font-semibold text-zinc-100 text-sm">Dove si concentrano le offerte</h3>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="w-3 h-0.5 bg-gold-400 inline-block rounded" />
          <span className="text-zinc-500">Fair Price: {fairPrice.toLocaleString('it-IT')} €</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={bins} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" vertical={false} />
          <XAxis
            dataKey="range"
            tick={{ fill: '#71717a', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#71717a', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
            width={28}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <ReferenceLine
            x={fairBinRange}
            stroke="#d4a82a"
            strokeWidth={2}
            strokeDasharray="4 3"
            label={{
              value: 'Fair',
              position: 'top',
              fill: '#d4a82a',
              fontSize: 10,
              fontWeight: 600,
            }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {bins.map((entry, index) => {
              const leftBound = parseFloat(entry.range.split('–')[0].replace(/[^\d]/g, ''))
              const isNearFair = Math.abs(leftBound - fairPrice) < (fairPrice * 0.08)
              return (
                <Cell
                  key={index}
                  fill={isNearFair ? '#d4a82a' : '#52525b'}
                  fillOpacity={isNearFair ? 0.9 : 0.7}
                />
              )
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Percentile bands legend */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-zinc-800 text-xs text-zinc-500">
        {Object.entries(distribution.percentile_bands).map(([key, val]) => (
          <div key={key} className="text-center">
            <p className="text-zinc-600 uppercase tracking-wider text-[10px]">{key}</p>
            <p className="text-zinc-300 font-semibold mt-0.5">{val.toLocaleString('it-IT')} €</p>
          </div>
        ))}
      </div>
    </div>
  )
}
