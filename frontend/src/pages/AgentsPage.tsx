import { useQuery } from '@tanstack/react-query'
import { getAgentsStatus } from '../lib/api'
import { Bot, CheckCircle, AlertCircle, TestTube } from 'lucide-react'
import { clsx } from 'clsx'

const AGENT_INFO: Record<string, { desc: string; sources: string[] }> = {
  marketplace_agent: {
    desc: 'Monitora i principali marketplace di orologi usati',
    sources: ['Chrono24', 'WatchBox', "Bob's Watches", 'Watchfinder', 'eBay'],
  },
  social_agent: {
    desc: 'Scannerizza post e stories dei reseller sui social',
    sources: ['Instagram', 'TikTok'],
  },
  vision_agent: {
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
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="font-display font-bold text-3xl text-zinc-100 mb-2">Agenti</h1>
      <p className="text-zinc-500 mb-8">Stato e configurazione degli agenti di scansione</p>

      {isLoading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton rounded-xl h-36" />)}
        </div>
      )}

      <div className="space-y-4">
        {agents?.map(agent => {
          const info = AGENT_INFO[agent.name]
          const StatusIcon = agent.status === 'ok' ? CheckCircle
            : agent.status === 'mock' ? TestTube
            : AlertCircle

          return (
            <div key={agent.name} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-gold-400/10 border border-gold-400/20 rounded-lg flex items-center justify-center mt-0.5">
                    <Bot size={18} className="text-gold-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-zinc-100">
                        {agent.name.replace('_agent', '').replace('_', ' ').replace(/^\w/, c => c.toUpperCase())} Agent
                      </h3>
                      <span className={clsx(
                        'flex items-center gap-1 text-xs rounded-full px-2 py-0.5 border',
                        agent.status === 'ok' ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' :
                        agent.status === 'mock' ? 'text-amber-400 bg-amber-400/10 border-amber-400/20' :
                        'text-red-400 bg-red-400/10 border-red-400/20'
                      )}>
                        <StatusIcon size={10} />
                        {agent.mock_mode ? 'Mock' : agent.status === 'ok' ? 'Attivo' : 'Errore'}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-500 mb-3">{info?.desc}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {info?.sources.map(s => (
                        <span key={s} className="text-xs text-zinc-400 bg-zinc-800 border border-zinc-700 rounded-full px-2.5 py-0.5">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              {agent.error && (
                <div className="mt-4 text-xs text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
                  {agent.error}
                </div>
              )}
              {agent.mock_mode && (
                <div className="mt-4 text-xs text-amber-400/80 bg-amber-400/5 border border-amber-400/10 rounded-lg px-3 py-2">
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
