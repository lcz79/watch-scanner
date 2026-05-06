import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { getCatalog } from '../lib/api'
import type { CatalogWatch } from '../lib/api'
import { clsx } from 'clsx'

export default function CatalogPage() {
  const navigate = useNavigate()
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['catalog', selectedBrand, search],
    queryFn: () => getCatalog({ brand: selectedBrand || undefined, search: search || undefined }),
    staleTime: 60_000,
  })

  return (
    <div className="p-8 max-w-[1400px] mx-auto">

      {/* ── Header ── */}
      <div className="mb-8">
        <nav className="flex text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-2 gap-2">
          <span className="hover:text-yellow-400 cursor-pointer">Market Intelligence</span>
          <span>/</span>
          <span className="text-zinc-300">Encyclopedia</span>
        </nav>
        <h2 className="font-h1 text-h1 text-zinc-100">Encyclopedia</h2>
        <p className="text-zinc-500 text-sm mt-1">
          Seleziona un orologio — cercheremo solo annunci per quel modello esatto
        </p>
      </div>

      {/* ── Search + brand filter ── */}
      <div className="bg-zinc-900 border border-zinc-800 p-4 mb-6 flex items-center justify-between flex-wrap gap-4">
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 text-sm leading-none">search</span>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Cerca referenza o modello..."
            className="bg-zinc-800 border border-zinc-700 text-sm pl-10 pr-4 py-2 w-72 rounded focus:outline-none focus:border-yellow-400 text-zinc-300 placeholder-zinc-600 transition-colors"
          />
        </div>

        <div className="flex gap-1.5 flex-wrap items-center">
          <button
            onClick={() => setSelectedBrand(null)}
            className={clsx('font-label-caps text-label-caps px-3 py-1.5 rounded border transition-colors uppercase',
              !selectedBrand ? 'bg-zinc-700 border-zinc-600 text-yellow-400' : 'bg-transparent border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200'
            )}
          >
            Tutti
          </button>
          {data?.brands.map(brand => (
            <button
              key={brand}
              onClick={() => setSelectedBrand(brand === selectedBrand ? null : brand)}
              className={clsx('font-label-caps text-label-caps px-3 py-1.5 rounded border transition-colors uppercase',
                brand === selectedBrand ? 'bg-zinc-700 border-zinc-600 text-yellow-400' : 'bg-transparent border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200'
              )}
            >
              {brand}
            </button>
          ))}
        </div>
      </div>

      {data && (
        <p className="font-label-caps text-label-caps text-zinc-500 uppercase mb-5">
          {data.total} modelli disponibili
        </p>
      )}

      {/* ── Loading ── */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <span className="material-symbols-outlined text-4xl text-yellow-400 animate-spin">autorenew</span>
        </div>
      )}

      {/* ── Grid ── */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-[12px]">
          {data.watches.map(watch => (
            <WatchCard key={watch.id} watch={watch} onSelect={w => navigate(`/encyclopedia/${encodeURIComponent(w.reference)}`)} />
          ))}
        </div>
      )}

      {data?.watches.length === 0 && (
        <div className="text-center py-20 bg-zinc-900 border border-zinc-800">
          <span className="material-symbols-outlined text-5xl text-zinc-700 block mb-4">watch_off</span>
          <p className="font-['Space_Grotesk'] font-semibold text-zinc-400">Nessun orologio trovato</p>
        </div>
      )}
    </div>
  )
}

function WatchCard({ watch, onSelect }: { watch: CatalogWatch; onSelect: (w: CatalogWatch) => void }) {
  const [imgError, setImgError] = useState(false)

  return (
    <button
      onClick={() => onSelect(watch)}
      className="group bg-zinc-900 border border-zinc-800 overflow-hidden hover:border-yellow-400/40 transition-colors text-left"
    >
      {/* Image */}
      <div className="aspect-square bg-zinc-800 relative overflow-hidden">
        {!imgError ? (
          <img
            src={watch.image_url}
            alt={watch.canonical_name}
            onError={() => setImgError(true)}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="material-symbols-outlined text-4xl text-zinc-700">watch</span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
          <span className="flex items-center gap-1 text-[10px] font-bold text-white uppercase tracking-widest">
            Apri scheda
            <span className="material-symbols-outlined text-sm leading-none">chevron_right</span>
          </span>
        </div>
      </div>

      {/* Info */}
      <div className="p-3 border-t border-zinc-800">
        <p className="font-label-caps text-label-caps text-zinc-500 uppercase mb-0.5">{watch.brand}</p>
        <p className="font-['Space_Grotesk'] text-sm font-semibold text-zinc-100 leading-tight">{watch.model}</p>
        <p className="font-mono-data text-mono-data text-yellow-400 mt-0.5">{watch.reference}</p>
        <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-1.5">
          ~{watch.avg_price_eur.toLocaleString('it-IT')}€
        </p>
      </div>
    </button>
  )
}
