import { useQuery } from '@tanstack/react-query'
import { getAgentsStatus } from '../lib/api'
import type { AgentStatus, AgentsStatusResponse } from '../types'
import { clsx } from 'clsx'
import { useLang } from '../lib/lang'

function normalizeAgents(data: AgentsStatusResponse | AgentStatus[] | undefined): AgentStatus[] {
  if (!data) return []
  if (Array.isArray(data)) return data
  return data.agents ?? []
}

const AGENT_INFO: Record<string, { sources: string[]; icon: string }> = {
  marketplace_agent: {
    icon: 'storefront',
    sources: ['Chrono24', 'WatchBox', "Bob's Watches", 'Watchfinder', 'eBay'],
  },
  social_agent: {
    icon: 'photo_camera',
    sources: ['Instagram', 'TikTok'],
  },
  vision_agent: {
    icon: 'visibility',
    sources: ['GPT-4o Vision'],
  },
}

export default function AgentsPage() {
  const { t } = useLang()

  const agentDescriptions: Record<string, string> = {
    marketplace_agent: t.agentDescMarketplace,
    social_agent: t.agentDescSocial,
    vision_agent: t.agentDescVision,
  }

  const { data: rawAgents, isLoading } = useQuery({
    queryKey: ['agents-status'],
    queryFn: getAgentsStatus,
    refetchInterval: 10_000,
  })

  const agentList = normalizeAgents(rawAgents)

  function getStatusProps(agent: AgentStatus) {
    const s = agent.mock_mode ? 'mock' : agent.status
    if (s === 'ok' || s === 'idle')
      return { icon: 'check_circle', cls: 'text-green-400 bg-green-400/10 border-green-400/20', dot: 'bg-green-400', label: t.agentStatusActive }
    if (s === 'running')
      return { icon: 'autorenew', cls: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20', dot: 'bg-yellow-400', label: t.agentStatusRunning }
    if (s === 'mock')
      return { icon: 'science', cls: 'text-amber-400 bg-amber-400/10 border-amber-400/20', dot: 'bg-amber-400', label: t.agentStatusMock }
    return { icon: 'error', cls: 'text-red-400 bg-red-400/10 border-red-400/20', dot: 'bg-red-400', label: t.agentStatusError }
  }

  return (
    <div className="p-8 max-w-[1400px] mx-auto">

      {/* ── Header ── */}
      <div className="mb-8">
        <nav className="flex text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2 gap-2">
          <span className="hover:text-yellow-400 cursor-pointer">{t.agentsSystem}</span>
          <span>/</span>
          <span className="text-zinc-300">{t.agentsNavAgents}</span>
        </nav>
        <h2 className="font-h1 text-h1 text-zinc-100">{t.agentsTitle}</h2>
        <p className="text-zinc-500 text-sm mt-1">{t.agentsSubtitle}</p>
      </div>

      {/* ── Loading skeleton ── */}
      {isLoading && (
        <div className="space-y-[4px]">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-36" />)}
        </div>
      )}

      {/* ── Agent cards ── */}
      <div className="space-y-[4px]">
        {agentList.map(agent => {
          const info = AGENT_INFO[agent.name]
          const { icon: statusIcon, cls: statusClass, dot: dotClass, label: statusLabel } = getStatusProps(agent)

          return (
            <div key={agent.name} className="bg-zinc-900 border border-zinc-800 p-[24px]">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className="w-12 h-12 bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-xl text-yellow-400 leading-none">
                      {info?.icon ?? 'smart_toy'}
                    </span>
                  </div>

                  <div>
                    {/* Name + status */}
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-h2 text-zinc-100" style={{ fontSize: '18px' }}>
                        {agent.name.replace('_agent', '').replace('_', ' ').replace(/^\w/, c => c.toUpperCase())} Agent
                      </h3>
                      <span className={clsx('flex items-center gap-1.5 text-[10px] font-bold border px-2 py-0.5 rounded uppercase', statusClass)}>
                        <span className={clsx('w-1.5 h-1.5 rounded-full shrink-0', dotClass)} />
                        <span className="material-symbols-outlined text-xs leading-none">{statusIcon}</span>
                        {statusLabel}
                      </span>
                    </div>

                    <p className="text-sm text-zinc-500 mb-3">{agentDescriptions[agent.name] ?? info?.sources.join(', ')}</p>

                    <div className="flex flex-wrap gap-1.5">
                      {info?.sources.map(s => (
                        <span key={s}
                          className="font-label-caps text-label-caps text-zinc-400 bg-zinc-800 border border-zinc-700 px-2.5 py-0.5 rounded uppercase">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Right: last_run + items_found */}
                <div className="text-right text-[11px] text-zinc-500 font-mono-data space-y-1 shrink-0">
                  {agent.items_found != null && (
                    <p><span className="text-zinc-300">{agent.items_found}</span> items</p>
                  )}
                  {agent.last_run && (
                    <p className="truncate max-w-[140px]">{new Date(agent.last_run).toLocaleTimeString()}</p>
                  )}
                </div>
              </div>

              {agent.error && (
                <div className="mt-4 flex items-start gap-2 text-xs text-red-400 bg-red-400/10 border border-red-400/20 px-3 py-2 rounded">
                  <span className="material-symbols-outlined text-sm leading-none shrink-0">error</span>
                  {agent.error}
                </div>
              )}

              {agent.mock_mode && (
                <div className="mt-4 flex items-start gap-2 text-xs text-amber-400/80 bg-amber-400/5 border border-amber-400/10 px-3 py-2 rounded">
                  <span className="material-symbols-outlined text-sm leading-none shrink-0">science</span>
                  {t.agentMockWarning}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
