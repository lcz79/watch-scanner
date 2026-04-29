import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Search, Watch, ChevronRight, Loader2 } from 'lucide-react'
import { getCatalog } from '../lib/api'
import type { CatalogWatch } from '../lib/api'
import { clsx } from 'clsx'

export default function CatalogPage() {
  const navigate = useNavigate()
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['catalog', selectedBrand, search],
    queryFn: () => getCatalog({
      brand: selectedBrand || undefined,
      search: search || undefined,
    }),
    staleTime: 60_000,
  })

  const handleSelect = (watch: CatalogWatch) => {
    // Vai alla pagina di ricerca con la referenza pre-compilata e avvia subito la scan
    navigate(`/search?ref=${watch.reference}`)
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">

      {/* Header */}
      <div className="mb-10">
        <h1 className="font-display font-bold text-3xl text-zinc-100 tracking-tight">
          Catalogo orologi
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Seleziona un orologio dalla foto — cercheremo solo annunci per quel modello esatto
        </p>
      </div>

      {/* Search + brand filter */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Cerca referenza o modello..."
            className="w-full bg-zinc-900 border border-zinc-700 rounded-xl pl-9 pr-4 py-2.5 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-gold-400 text-sm"
          />
        </div>

        {/* Brand pills */}
        <div className="flex gap-2 flex-wrap items-center">
          <button
            onClick={() => setSelectedBrand(null)}
            className={clsx(
              'text-xs px-3 py-2 rounded-lg border transition-colors',
              !selectedBrand
                ? 'bg-gold-400/20 border-gold-400 text-gold-400'
                : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
            )}
          >
            Tutti
          </button>
          {data?.brands.map(brand => (
            <button
              key={brand}
              onClick={() => setSelectedBrand(brand === selectedBrand ? null : brand)}
              className={clsx(
                'text-xs px-3 py-2 rounded-lg border transition-colors',
                brand === selectedBrand
                  ? 'bg-gold-400/20 border-gold-400 text-gold-400'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              )}
            >
              {brand}
            </button>
          ))}
        </div>
      </div>

      {/* Count */}
      {data && (
        <p className="text-xs text-zinc-600 mb-5">
          {data.total} modelli disponibili
        </p>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="animate-spin text-gold-400" size={28} />
        </div>
      )}

      {/* Grid */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {data.watches.map(watch => (
            <WatchCard key={watch.id} watch={watch} onSelect={handleSelect} />
          ))}
        </div>
      )}

      {data?.watches.length === 0 && (
        <div className="text-center py-20 text-zinc-500">
          <Watch size={36} className="mx-auto mb-3 opacity-30" />
          <p>Nessun orologio trovato</p>
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
      className="group bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden hover:border-gold-400/50 hover:shadow-lg hover:shadow-black/40 transition-all duration-200 text-left"
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
            <Watch size={32} className="text-zinc-700" />
          </div>
        )}
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
          <span className="flex items-center gap-1 text-xs font-medium text-white">
            Cerca annunci <ChevronRight size={12} />
          </span>
        </div>
      </div>

      {/* Info */}
      <div className="p-3">
        <p className="text-xs text-zinc-500 mb-0.5">{watch.brand}</p>
        <p className="text-sm font-semibold text-zinc-100 leading-tight">{watch.model}</p>
        <p className="text-xs text-gold-400 font-mono mt-0.5">{watch.reference}</p>
        <p className="text-xs text-zinc-600 mt-1.5">
          ~{watch.avg_price_eur.toLocaleString('it-IT')}€
        </p>
      </div>
    </button>
  )
}
