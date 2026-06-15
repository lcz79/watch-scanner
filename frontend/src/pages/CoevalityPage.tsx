import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { clsx } from 'clsx'
import { checkCoevality, getCoevalityReferences } from '../lib/api'
import type { CoevalityResult, CoevalVariant } from '../lib/api'

const EXAMPLE = 'U543456'

const CONFIDENCE: Record<string, { label: string; cls: string }> = {
  alta:  { label: 'Confidenza alta',  cls: 'text-green-400 bg-green-400/10 border-green-400/20' },
  media: { label: 'Confidenza media', cls: 'text-amber-400 bg-amber-400/10 border-amber-400/20' },
  bassa: { label: 'Da verificare',    cls: 'text-zinc-400 bg-zinc-400/10 border-zinc-400/20' },
}

function VariantRow({ v, coeval }: { v: CoevalVariant; coeval: boolean }) {
  const conf = CONFIDENCE[v.confidence] ?? CONFIDENCE.bassa
  const span = v.year_from === v.year_to ? `${v.year_from}` : `${v.year_from}–${v.year_to}`
  return (
    <div className={clsx(
      'flex gap-3 p-3 border rounded',
      coeval ? 'bg-green-900/10 border-green-700/30' : 'bg-zinc-950/40 border-zinc-800 opacity-60'
    )}>
      <div className="mt-0.5">
        <span className={clsx('material-symbols-outlined text-base leading-none',
          coeval ? 'text-green-400' : 'text-zinc-600')}>
          {coeval ? 'check_circle' : 'remove'}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-sm">{v.label}</span>
          <span className="font-mono-data text-[10px] text-zinc-500">{span}</span>
          {coeval && (
            <span className={clsx('px-1.5 py-0.5 text-[9px] font-bold uppercase border rounded', conf.cls)}>
              {conf.label}
            </span>
          )}
        </div>
        <p className="text-xs text-zinc-400 mt-1 leading-snug">{v.description}</p>
      </div>
    </div>
  )
}

export default function CoevalityPage() {
  const [serial, setSerial] = useState('')
  const [reference, setReference] = useState('16520')
  const [result, setResult] = useState<CoevalityResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { data: refs = [] } = useQuery({
    queryKey: ['coevality-refs'],
    queryFn: getCoevalityReferences,
    staleTime: 60 * 60 * 1000,
  })

  const { mutate, isPending } = useMutation({
    mutationFn: () => checkCoevality(serial.trim(), reference),
    onSuccess: (d) => { setResult(d); setError(null) },
    onError: (e: any) => {
      setResult(null)
      setError(e?.response?.data?.detail || e?.message || 'Errore durante il controllo')
    },
  })

  const run = (s?: string) => {
    const target = (s ?? serial).trim()
    if (!target) return
    if (s) setSerial(s)
    setError(null)
    mutate()
  }

  const est = result?.serial_estimate
  const dated = !!est?.year_from

  return (
    <div className="p-8 max-w-[1100px] mx-auto">
      {/* Header */}
      <div className="mb-8">
        <nav className="flex text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2 gap-2">
          <span>Autenticazione</span><span>/</span><span className="text-zinc-300">Controllo Coevità</span>
        </nav>
        <h2 className="font-h1 text-h1 text-zinc-100">Controllo Coevità</h2>
        <p className="text-sm text-zinc-500 mt-2 max-w-2xl">
          Inserisci il numero di serie: dal seriale stimiamo l'anno e ti diciamo quali
          componenti (quadrante, ghiera, bracciale, calibro…) sono <em>coevi</em> con quell'anno.
        </p>
      </div>

      {/* Form */}
      <div className="bg-zinc-900 border border-zinc-800 p-6 mb-8">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-end">
          <div className="flex-1">
            <label className="font-label-caps text-[11px] text-zinc-400 uppercase mb-2 block flex items-center gap-1.5">
              <span className="material-symbols-outlined text-sm leading-none text-yellow-400">tag</span>
              Numero di serie
            </label>
            <input
              value={serial}
              onChange={e => setSerial(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && run()}
              placeholder={`es. ${EXAMPLE}`}
              className="w-full bg-zinc-800 border border-zinc-700 rounded px-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-yellow-400 transition-colors text-base font-mono-data uppercase"
            />
          </div>
          <div className="sm:w-52">
            <label className="font-label-caps text-[11px] text-zinc-400 uppercase mb-2 block">Referenza</label>
            <select
              value={reference}
              onChange={e => setReference(e.target.value)}
              className="w-full bg-zinc-800 border border-zinc-700 rounded px-4 py-3 text-zinc-100 focus:outline-none focus:border-yellow-400 transition-colors text-sm"
            >
              {(refs.length ? refs : [{ reference: '16520', model: 'Rolex Daytona 16520', production_from: 1988, production_to: 2000 }]).map(r => (
                <option key={r.reference} value={r.reference}>{r.reference} — {r.model}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => run()}
            disabled={isPending || !serial.trim()}
            className="flex items-center justify-center gap-2 rounded px-6 py-3 font-bold text-sm uppercase tracking-widest bg-primary text-on-primary hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            {isPending
              ? <span className="material-symbols-outlined text-base leading-none animate-spin">autorenew</span>
              : <span className="material-symbols-outlined text-base leading-none">fact_check</span>}
            Analizza
          </button>
        </div>
        <div className="flex items-center gap-2 mt-3">
          <span className="font-label-caps text-[11px] text-zinc-500 uppercase">Prova:</span>
          <button onClick={() => run(EXAMPLE)} disabled={isPending}
            className="text-xs px-3 py-1 rounded bg-zinc-800 border border-zinc-700 text-zinc-400 hover:border-yellow-400/50 hover:text-yellow-400 transition-all disabled:opacity-40 font-mono-data">
            {EXAMPLE}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 bg-red-900/20 border border-red-700/40 p-4 mb-6 text-red-300 text-sm rounded">
          <span className="material-symbols-outlined text-lg leading-none text-red-400 shrink-0">warning</span>
          <span>{error}</span>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-6">
          {/* Serial estimate banner */}
          <div className={clsx('border p-5 rounded',
            dated ? 'bg-zinc-900 border-yellow-400/30' : 'bg-zinc-900 border-zinc-800')}>
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <p className="font-label-caps text-[10px] text-zinc-500 uppercase tracking-widest mb-1">{result.model}</p>
                <div className="flex items-baseline gap-3">
                  <span className="font-mono-data text-lg text-zinc-300">{est?.serial}</span>
                  {dated && <span className="material-symbols-outlined text-zinc-600">arrow_forward</span>}
                  {dated && (
                    <span className="font-display-price text-3xl text-yellow-400 leading-none">
                      {est?.year_from === est?.year_to ? est?.year_from : `${est?.year_from}–${est?.year_to}`}
                    </span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <p className="font-label-caps text-[9px] text-zinc-600 uppercase">Produzione referenza</p>
                <p className="font-mono-data text-sm text-zinc-400">{result.production_from}–{result.production_to}</p>
              </div>
            </div>
            <p className="text-xs text-zinc-500 mt-3 flex items-start gap-2">
              <span className="material-symbols-outlined text-sm leading-none text-zinc-600 shrink-0">info</span>
              {est?.note}
            </p>
          </div>

          {/* Components */}
          {dated ? (
            <div className="grid md:grid-cols-2 gap-4">
              {result.components.map((c, i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 p-5 rounded">
                  <div className="flex items-center gap-2 mb-3 pb-3 border-b border-zinc-800">
                    <span className="material-symbols-outlined text-yellow-400">{c.icon}</span>
                    <h3 className="font-['Space_Grotesk'] font-semibold text-zinc-100">{c.component}</h3>
                  </div>
                  <div className="space-y-2">
                    {c.coeval.length === 0 && (
                      <p className="text-xs text-zinc-500 italic">Nessuna variante documentata per quest'anno.</p>
                    )}
                    {c.coeval.map((v, j) => <VariantRow key={`co-${j}`} v={v} coeval />)}
                    {c.other_variants.map((v, j) => <VariantRow key={`ot-${j}`} v={v} coeval={false} />)}
                  </div>
                  {c.note && <p className="text-[11px] text-zinc-500 mt-3 italic">{c.note}</p>}
                  {c.sources.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {c.sources.map((s, k) => (
                        <a key={k} href={s.url} target="_blank" rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-[10px] text-zinc-500 hover:text-yellow-400 transition-colors">
                          <span className="material-symbols-outlined text-[11px]">open_in_new</span>
                          {s.name}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded text-center">
              <span className="material-symbols-outlined text-4xl text-zinc-700 block mb-2">help</span>
              <p className="text-sm text-zinc-400">Anno non stimabile da questo seriale — vedi la nota qui sopra.</p>
            </div>
          )}

          {/* Disclaimer */}
          <div className="bg-zinc-950/60 border border-zinc-800 p-4 rounded">
            <p className="text-[11px] text-zinc-500 leading-relaxed flex items-start gap-2">
              <span className="material-symbols-outlined text-sm leading-none text-zinc-600 shrink-0">gavel</span>
              {result.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
