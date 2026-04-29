import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Globe, Camera, Bell, ChevronRight, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getRecommendations } from '../lib/api'
import type { Recommendation, InvestmentScore } from '../types'

const POPULAR_REFS = ['116610LN', '126710BLNR', '5711/1A', '116500LN', '15500ST', '126334']

const STEPS = [
  {
    number: '01',
    icon: Search,
    title: 'Inserisci la referenza',
    desc: 'Scrivi il codice modello (es. 116610LN) o il nome del modello. Il sistema riconosce sia referenze che nomi commerciali.',
  },
  {
    number: '02',
    icon: Globe,
    title: 'Gli agenti scansionano',
    desc: 'Chrono24, eBay, Instagram e altri marketplace vengono analizzati in parallelo con tecnologia anti-bot avanzata.',
  },
  {
    number: '03',
    icon: Bell,
    title: 'Ricevi il miglior prezzo',
    desc: 'I risultati vengono aggregati e ordinati per prezzo crescente. Imposta un alert per essere notificato via email.',
  },
]

const AGENTS = [
  {
    icon: Globe,
    color: 'blue',
    title: 'Marketplace Agent',
    desc: 'Scansiona Chrono24 e eBay con tecnologia anti-bot avanzata, estraendo prezzi, condizioni e venditori verificati.',
  },
  {
    icon: Camera,
    color: 'purple',
    title: 'Social Agent',
    desc: 'Monitora i reseller su Instagram, analizza le stories con OCR per rilevare referenze e prezzi nascosti nelle immagini.',
  },
  {
    icon: Bell,
    color: 'gold',
    title: 'Alert Agent',
    desc: 'Controlla i prezzi ogni 30 minuti e invia una notifica email non appena il tuo orologio scende sotto la soglia impostata.',
  },
]

const STATS = [
  { value: '50+', label: 'Annunci per ricerca' },
  { value: '30 min', label: 'Frequenza alert' },
  { value: '100%', label: 'Gratuito' },
]

const agentIconColor: Record<string, string> = {
  blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
  purple: 'bg-purple-500/10 border-purple-500/20 text-purple-400',
  gold: 'bg-gold-400/10 border-gold-400/20 text-gold-400',
}

// ─── Recommendation section helpers ──────────────────────────────────────────

const SIGNAL_BADGE: Record<InvestmentScore['signal'], { label: string; cls: string }> = {
  buy:   { label: 'BUY',   cls: 'bg-green-500/15 border-green-500/30 text-green-400' },
  hold:  { label: 'HOLD',  cls: 'bg-yellow-500/15 border-yellow-500/30 text-yellow-400' },
  avoid: { label: 'AVOID', cls: 'bg-red-500/15 border-red-500/30 text-red-400' },
}

function TrendIcon({ trend }: { trend: InvestmentScore['trend'] }) {
  if (trend === 'up')   return <TrendingUp   size={13} className="text-green-400" />
  if (trend === 'down') return <TrendingDown  size={13} className="text-red-400" />
  return                       <Minus         size={13} className="text-zinc-500" />
}

function RecommendationCard({ rec, onSearch }: { rec: Recommendation; onSearch: (ref: string) => void }) {
  const signal = SIGNAL_BADGE[rec.investment.signal]
  return (
    <button
      onClick={() => onSearch(rec.reference)}
      className="group text-left bg-zinc-900 border border-zinc-800 rounded-2xl p-6 hover:border-zinc-700 hover:scale-[1.02] transition-all duration-200 w-full"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="font-display font-bold text-gold-400 text-xl tracking-tight">{rec.reference}</p>
          <div className="flex items-center gap-1.5 mt-1">
            <TrendIcon trend={rec.investment.trend} />
            <span className="text-xs text-zinc-500 capitalize">
              {rec.investment.trend === 'up' ? 'In salita' : rec.investment.trend === 'down' ? 'In discesa' : 'Stabile'}
            </span>
          </div>
        </div>
        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-bold tracking-widest ${signal.cls}`}>
          {signal.label}
        </span>
      </div>

      {/* Fair price */}
      <div className="mb-3">
        <p className="text-xs text-zinc-500 mb-0.5">Fair Price</p>
        <p className="font-semibold text-zinc-100 text-lg">
          {rec.market_stats.fair_price.toLocaleString('it-IT')} €
        </p>
      </div>

      {/* Best deal */}
      {rec.top_deal && (
        <div className="bg-zinc-800/60 rounded-xl px-3 py-2 flex items-center justify-between">
          <span className="text-xs text-zinc-500">Miglior offerta</span>
          <span className="text-xs font-bold text-green-400">
            {rec.top_deal.price.toLocaleString('it-IT')} €
          </span>
        </div>
      )}

      {/* Score */}
      <div className="mt-3 flex items-center justify-between text-xs text-zinc-600">
        <span>Score</span>
        <span className="font-semibold text-gold-400">{rec.global_score.toFixed(0)}/100</span>
      </div>

      <div className="mt-3 text-xs text-zinc-600 group-hover:text-gold-400 transition-colors flex items-center gap-1">
        Cerca ora <ChevronRight size={12} />
      </div>
    </button>
  )
}

function SkeletonCard() {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 animate-pulse">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="h-5 w-24 bg-zinc-800 rounded mb-2" />
          <div className="h-3 w-16 bg-zinc-800 rounded" />
        </div>
        <div className="h-5 w-14 bg-zinc-800 rounded-full" />
      </div>
      <div className="h-3 w-16 bg-zinc-800 rounded mb-1" />
      <div className="h-5 w-28 bg-zinc-800 rounded mb-3" />
      <div className="h-8 bg-zinc-800 rounded-xl" />
    </div>
  )
}

function RecommendationsSection({ onSearch }: { onSearch: (ref: string) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  })

  // Don't render if loaded but empty
  if (!isLoading && (!data || data.length === 0)) return null

  return (
    <section className="max-w-4xl mx-auto px-6 py-12">
      <div className="mb-6">
        <h2 className="font-display font-bold text-2xl text-zinc-100 mb-1">
          Opportunità del momento
        </h2>
        <p className="text-zinc-500 text-sm">Referenze con il miglior rapporto qualità/prezzo ora sul mercato.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {isLoading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          (data ?? []).slice(0, 3).map((rec: Recommendation) => (
            <RecommendationCard key={rec.reference} rec={rec} onSearch={onSearch} />
          ))
        )}
      </div>
    </section>
  )
}

// ─── HomePage ─────────────────────────────────────────────────────────────────

export default function HomePage() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSearch = () => {
    const val = query.trim()
    if (val) navigate(`/search?ref=${encodeURIComponent(val)}`)
    else navigate('/search')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="min-h-screen bg-zinc-950">

      {/* HERO */}
      <section className="relative flex flex-col items-center justify-center text-center px-6 pt-24 pb-20 overflow-hidden">
        {/* Radial glow behind search */}
        <div
          aria-hidden
          style={{
            position: 'absolute',
            top: '55%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '700px',
            height: '340px',
            background: 'radial-gradient(ellipse at center, rgba(212,168,42,0.12) 0%, transparent 70%)',
            pointerEvents: 'none',
          }}
        />

        {/* Badge */}
        <div
          style={{ opacity: 0, animation: 'fadeIn 0.5s ease forwards 0.1s' }}
          className="inline-flex items-center gap-2 text-xs text-gold-400 border border-gold-400/30 rounded-full px-4 py-1.5 mb-8 bg-gold-400/5"
        >
          <span className="w-1.5 h-1.5 bg-gold-400 rounded-full pulse-dot" />
          Sistema agentico attivo
        </div>

        {/* Title */}
        <h1
          style={{ opacity: 0, animation: 'fadeIn 0.6s ease forwards 0.2s' }}
          className="font-display font-bold text-6xl md:text-7xl text-zinc-100 leading-tight mb-6 max-w-3xl"
        >
          Trova il tuo orologio
          <br />
          al{' '}
          <span className="text-gold-400">miglior prezzo</span>
        </h1>

        {/* Subtitle */}
        <p
          style={{ opacity: 0, animation: 'fadeIn 0.6s ease forwards 0.35s' }}
          className="text-zinc-400 text-lg md:text-xl max-w-xl mx-auto mb-10 leading-relaxed"
        >
          Agenti AI che scansionano marketplace, social e reseller in parallelo.
          Stessa referenza, prezzo più basso garantito.
        </p>

        {/* Search bar */}
        <div
          style={{ opacity: 0, animation: 'fadeIn 0.6s ease forwards 0.45s' }}
          className="w-full max-w-xl mx-auto mb-5"
        >
          <div className="flex items-center gap-0 bg-zinc-900 border border-zinc-700 rounded-2xl overflow-hidden focus-within:ring-2 focus-within:ring-gold-400/50 focus-within:border-gold-400/60 transition-all duration-200">
            <Search size={18} className="ml-5 text-zinc-500 flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="es. 116610LN, Daytona, Nautilus"
              className="flex-1 bg-transparent px-4 py-4 text-zinc-100 placeholder-zinc-500 focus:outline-none text-base"
            />
            <button
              onClick={handleSearch}
              className="bg-gold-400 text-zinc-900 font-semibold px-6 py-4 text-sm hover:bg-gold-500 active:bg-gold-600 transition-colors duration-150 flex-shrink-0"
            >
              Cerca
            </button>
          </div>
        </div>

        {/* Popular chips */}
        <div
          style={{ opacity: 0, animation: 'fadeIn 0.6s ease forwards 0.55s' }}
          className="flex items-center justify-center gap-2 flex-wrap"
        >
          <span className="text-xs text-zinc-600">Popolari:</span>
          {POPULAR_REFS.map(ref => (
            <button
              key={ref}
              onClick={() => navigate(`/search?ref=${encodeURIComponent(ref)}`)}
              className="text-xs text-zinc-400 bg-zinc-800 border border-zinc-700 rounded-full px-3 py-1 hover:border-gold-400/50 hover:text-gold-400 transition-colors duration-150"
            >
              {ref}
            </button>
          ))}
        </div>
      </section>

      {/* RECOMMENDATIONS */}
      <RecommendationsSection
        onSearch={(ref) => navigate(`/search?ref=${encodeURIComponent(ref)}`)}
      />

      {/* STATS BAR */}
      <section className="bg-zinc-900/60 border-y border-zinc-800">
        <div className="max-w-4xl mx-auto px-6 py-8 grid grid-cols-3 divide-x divide-zinc-800">
          {STATS.map(({ value, label }) => (
            <div key={label} className="text-center px-4">
              <p className="font-display font-bold text-3xl text-gold-400 mb-1">{value}</p>
              <p className="text-xs text-zinc-500">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="max-w-4xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h2 className="font-display font-bold text-3xl text-zinc-100 mb-3">Come funziona</h2>
          <p className="text-zinc-500 text-sm max-w-md mx-auto">
            Tre passi per trovare il prezzo più basso sul mercato.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {STEPS.map(({ number, icon: Icon, title, desc }) => (
            <div
              key={number}
              className="relative bg-zinc-900 border border-zinc-800 rounded-2xl p-6 hover:border-zinc-700 hover:scale-105 transition-transform duration-200"
            >
              <span className="font-display font-bold text-5xl text-zinc-800 absolute top-4 right-5 select-none leading-none">
                {number}
              </span>
              <div className="w-11 h-11 bg-gold-400/10 border border-gold-400/20 rounded-xl flex items-center justify-center mb-5">
                <Icon size={20} className="text-gold-400" />
              </div>
              <h3 className="font-semibold text-zinc-100 text-sm mb-2">{title}</h3>
              <p className="text-xs text-zinc-500 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* AGENTS */}
      <section className="bg-zinc-900/40 border-y border-zinc-800">
        <div className="max-w-4xl mx-auto px-6 py-20">
          <div className="text-center mb-12">
            <h2 className="font-display font-bold text-3xl text-zinc-100 mb-3">Agenti specializzati</h2>
            <p className="text-zinc-500 text-sm max-w-md mx-auto">
              Ogni agente si occupa di una fonte diversa, tutto in parallelo.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {AGENTS.map(({ icon: Icon, color, title, desc }) => (
              <div
                key={title}
                className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 hover:border-zinc-700 hover:scale-105 transition-transform duration-200"
              >
                <div className={`w-12 h-12 border rounded-xl flex items-center justify-center mb-5 ${agentIconColor[color]}`}>
                  <Icon size={22} />
                </div>
                <h3 className="font-semibold text-zinc-100 text-sm mb-2">{title}</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA FINALE */}
      <section className="max-w-4xl mx-auto px-6 py-20">
        <div
          className="rounded-2xl border border-gold-400/20 p-10 text-center"
          style={{ background: 'linear-gradient(135deg, rgba(212,168,42,0.08) 0%, rgba(212,168,42,0.03) 100%)' }}
        >
          <h2 className="font-display font-bold text-3xl text-zinc-100 mb-3">
            Pronto a trovare il tuo prossimo orologio?
          </h2>
          <p className="text-zinc-400 text-sm mb-8 max-w-sm mx-auto">
            Inserisci la referenza e lascia che gli agenti facciano il lavoro per te.
          </p>
          <button
            onClick={() => {
              window.scrollTo({ top: 0, behavior: 'smooth' })
              setTimeout(() => inputRef.current?.focus(), 400)
            }}
            className="inline-flex items-center gap-2 bg-gold-400 text-zinc-900 font-semibold px-8 py-3.5 rounded-xl hover:bg-gold-500 active:bg-gold-600 transition-colors duration-150"
          >
            Inizia la ricerca
            <ChevronRight size={16} />
          </button>
        </div>
      </section>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
