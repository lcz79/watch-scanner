import { useQuery } from '@tanstack/react-query'
import { getAgentsStatus } from '../lib/api'
import { clsx } from 'clsx'

const AGENT_INFO: Record<string, { desc: string; sources: string[]; icon: string }> = {
  marketplace_agent: {
    icon: 'storefront',
    desc: 'Monitora i principali marketplace di orologi usati',
    sources: ['Chrono24', 'WatchBox', "Bob's Watches", 'Watchfinder', 'eBay'],
  },
  social_agent: {
    icon: 'photo_camera',
    desc: 'Scannerizza post e stories dei reseller sui social',
    sources: ['Instagram', 'TikTok'],
  },
  vision_agent: {
    icon: 'visibility',
    desc: 'Analizza immagini con GPT-4o per identificare referenze e prezzi',
    sources: ['GPT-4o Vision'],
  },
}

export default function AgentsPage() {
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents-status'],
    queryFn: getAgentsStatus,
    refetchInterval: 10_000,
  })

  return (
    <div className="p-8 max-w-[1400px] mx-auto">

      {/* ── Header ── */}
      <div className="mb-8">
        <nav className="flex text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2 gap-2">
          <span className="hover:text-yellow-400 cursor-pointer">Sistema</span>
          <span>/</span>
          <span className="text-zinc-300">Agenti</span>
        </nav>
        <h2 className="font-h1 text-h1 text-zinc-100">Agenti di Scansione</h2>
        <p className="text-zinc-500 text-sm mt-1">Stato e configurazione degli agenti attivi</p>
      </div>

      {/* ── Loading skeleton ── */}
      {isLoading && (
        <div className="space-y-[4px]">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-36" />)}
        </div>
      )}

      {/* ── Agent cards ── */}
      <div className="space-y-[4px]">
        {agents?.map(agent => {
          const info = AGENT_INFO[agent.name]
          const statusIcon = agent.status === 'ok' ? 'check_circle' : agent.status === 'mock' ? 'science' : 'error'
          const statusClass = agent.status === 'ok'
            ? 'text-green-400 bg-green-400/10 border-green-400/20'
            : agent.status === 'mock'
            ? 'text-amber-400 bg-amber-400/10 border-amber-400/20'
            : 'text-red-400 bg-red-400/10 border-red-400/20'

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
                      <span className={clsx('flex items-center gap-1 text-[10px] font-bold border px-2 py-0.5 rounded uppercase', statusClass)}>
                        <span className="material-symbols-outlined text-xs leading-none">{statusIcon}</span>
                        {agent.mock_mode ? 'Mock' : agent.status === 'ok' ? 'Attivo' : 'Errore'}
                      </span>
                    </div>

                    <p className="text-sm text-zinc-500 mb-3">{info?.desc}</p>

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
                  Modalità mock attiva — configura le API key nel file .env per abilitare lo scraping reale
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
