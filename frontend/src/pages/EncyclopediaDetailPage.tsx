import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getEncyclopediaWatch, getAuctionResults, getAuctionSentiment } from '../lib/api'
import { clsx } from 'clsx'

export default function EncyclopediaDetailPage() {
  const { reference } = useParams<{ reference: string }>()
  const navigate = useNavigate()
  const ref = decodeURIComponent(reference ?? '')

  const { data: watch, isLoading, error } = useQuery({
    queryKey: ['encyclopedia', ref],
    queryFn: () => getEncyclopediaWatch(ref),
    enabled: !!ref,
    retry: 1,
  })

  const { data: auctionData } = useQuery({
    queryKey: ['auctions', ref],
    queryFn: () => getAuctionResults(ref, { limit: 5 }),
    enabled: !!ref,
  })

  const { data: sentiment } = useQuery({
    queryKey: ['auction-sentiment', ref],
    queryFn: () => getAuctionSentiment(ref),
    enabled: !!ref,
  })

  if (isLoading) {
    return (
      <div className="p-8 max-w-[1400px] mx-auto">
        <div className="flex items-center justify-center py-32">
          <span className="material-symbols-outlined text-4xl text-yellow-400 animate-spin">autorenew</span>
        </div>
      </div>
    )
  }

  if (error || !watch) {
    return (
      <div className="p-8 max-w-[1400px] mx-auto">
        <div className="text-center py-20 bg-zinc-900 border border-zinc-800">
          <span className="material-symbols-outlined text-5xl text-zinc-700 block mb-4">watch_off</span>
          <p className="font-['Space_Grotesk'] font-semibold text-zinc-400">Referenza non trovata nell'enciclopedia</p>
          <p className="text-xs text-zinc-600 mt-1">{ref}</p>
          <button
            onClick={() => navigate('/catalog')}
            className="mt-6 px-4 py-2 bg-zinc-800 text-zinc-300 text-sm rounded hover:bg-zinc-700 transition-colors"
          >
            Torna al catalogo
          </button>
        </div>
      </div>
    )
  }

  const primaryImage = watch.images.find(i => i.is_primary)?.url ?? watch.images[0]?.url

  const sentimentColor = sentiment?.sentiment_label === 'bullish' || sentiment?.sentiment_label === 'very_bullish'
    ? 'text-green-400 bg-green-400/10 border-green-400/20'
    : sentiment?.sentiment_label === 'bearish' || sentiment?.sentiment_label === 'very_bearish'
    ? 'text-red-400 bg-red-400/10 border-red-400/20'
    : 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'

  return (
    <div className="p-8 max-w-[1400px] mx-auto">

      {/* Breadcrumb */}
      <nav className="flex text-[10px] uppercase tracking-[0.2em] text-zinc-500 mb-6 gap-2 items-center">
        <span className="hover:text-yellow-400 cursor-pointer" onClick={() => navigate('/')}>Market Intelligence</span>
        <span>/</span>
        <span className="hover:text-yellow-400 cursor-pointer" onClick={() => navigate('/catalog')}>Encyclopedia</span>
        <span>/</span>
        <span className="text-zinc-300">{watch.reference}</span>
      </nav>

      {/* Hero */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-[12px] mb-[12px]">

        {/* Image */}
        <div className="bg-zinc-900 border border-zinc-800 aspect-square flex items-center justify-center overflow-hidden">
          {primaryImage ? (
            <img src={primaryImage} alt={watch.model} className="w-full h-full object-cover" />
          ) : (
            <span className="material-symbols-outlined text-6xl text-zinc-700">watch</span>
          )}
        </div>

        {/* Main info */}
        <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800 p-[24px]">
          <div className="flex items-start justify-between mb-4 gap-4">
            <div>
              <p className="font-label-caps text-label-caps text-zinc-500 uppercase mb-1">{watch.brand}</p>
              <h1 className="font-h1 text-h1 text-zinc-100 mb-1">{watch.model}</h1>
              <p className="font-mono-data text-mono-data text-yellow-400">{watch.reference}</p>
            </div>
            <div className="flex flex-col items-end gap-2 shrink-0">
              {watch.is_discontinued && (
                <span className="font-label-caps text-label-caps text-zinc-500 bg-zinc-800 border border-zinc-700 px-2.5 py-1 rounded uppercase">
                  Discontinuato
                </span>
              )}
              {watch.is_limited_edition && (
                <span className="font-label-caps text-label-caps text-yellow-400 bg-yellow-400/10 border border-yellow-400/20 px-2.5 py-1 rounded uppercase">
                  Limited Edition
                </span>
              )}
            </div>
          </div>

          {/* Price row */}
          <div className="flex gap-[12px] mb-5">
            {watch.retail_price_eur && (
              <div className="bg-zinc-800/40 border border-zinc-700/40 p-[24px] flex-1">
                <p className="font-label-caps text-label-caps text-zinc-500 uppercase mb-1">Retail</p>
                <p className="font-display-price text-2xl text-zinc-100">{watch.retail_price_eur.toLocaleString('it-IT')} €</p>
              </div>
            )}
            {watch.avg_market_price_eur && (
              <div className="bg-zinc-800/40 border border-zinc-700/40 p-[24px] flex-1">
                <p className="font-label-caps text-label-caps text-zinc-500 uppercase mb-1">Mercato</p>
                <p className="font-display-price text-2xl text-yellow-400">{watch.avg_market_price_eur.toLocaleString('it-IT')} €</p>
              </div>
            )}
            {sentiment && (
              <div className="bg-zinc-800/40 border border-zinc-700/40 p-[24px] flex-1">
                <p className="font-label-caps text-label-caps text-zinc-500 uppercase mb-1">Sentiment Aste</p>
                <span className={clsx('font-label-caps text-label-caps border px-2.5 py-1 rounded uppercase', sentimentColor)}>
                  {sentiment.sentiment_label ?? 'N/D'}
                </span>
              </div>
            )}
          </div>

          {/* Description */}
          {watch.description && (
            <p className="text-sm text-zinc-400 leading-relaxed mb-4">{watch.description}</p>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/search?ref=${watch.reference}`)}
              className="flex items-center gap-2 bg-primary text-on-primary font-bold px-5 py-2.5 rounded text-xs uppercase tracking-widest hover:opacity-90 transition-opacity"
            >
              <span className="material-symbols-outlined text-base leading-none">query_stats</span>
              Cerca il miglior prezzo
            </button>
            <button
              onClick={() => navigate(`/verify?ref=${watch.reference}`)}
              className="flex items-center gap-2 bg-zinc-800 text-zinc-300 font-bold px-5 py-2.5 rounded text-xs uppercase tracking-widest hover:bg-zinc-700 transition-colors border border-zinc-700"
            >
              <span className="material-symbols-outlined text-base leading-none">verified</span>
              Verifica autenticità
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-[12px] mb-[12px]">

        {/* Technical specs */}
        <div className="bg-zinc-900 border border-zinc-800 p-[24px]">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-4">Caratteristiche Tecniche</p>
          <div className="space-y-2">
            <SpecRow label="Collezione" value={watch.collection} />
            <SpecRow label="Anno introduzione" value={watch.year_introduced?.toString()} />
            {watch.year_discontinued && <SpecRow label="Anno fine produzione" value={watch.year_discontinued.toString()} />}
            <SpecRow label="Materiale cassa" value={watch.case_material} />
            <SpecRow label="Diametro" value={watch.case_diameter_mm ? `${watch.case_diameter_mm} mm` : null} />
            <SpecRow label="Spessore" value={watch.case_thickness_mm ? `${watch.case_thickness_mm} mm` : null} />
            <SpecRow label="Impermeabilità" value={watch.water_resistance_m ? `${watch.water_resistance_m} m` : null} />
            <SpecRow label="Movimento" value={watch.movement_type} />
            <SpecRow label="Calibro" value={watch.movement_caliber} />
            <SpecRow label="Riserva di carica" value={watch.power_reserve_h ? `${watch.power_reserve_h} ore` : null} />
            <SpecRow label="Frequenza" value={watch.frequency_vph ? `${watch.frequency_vph} vph` : null} />
            <SpecRow label="Rubini" value={watch.jewels?.toString()} />
            <SpecRow label="Quadrante" value={watch.dial_color} />
            <SpecRow label="Materiale quadrante" value={watch.dial_material} />
            <SpecRow label="Bracciale" value={watch.bracelet_type} />
            <SpecRow label="Chiusura" value={watch.clasp_type} />
            {watch.is_limited_edition && watch.production_numbers && (
              <SpecRow label="Esemplari prodotti" value={watch.production_numbers.toLocaleString('it-IT')} />
            )}
          </div>
        </div>

        {/* Technical notes + auction sentiment */}
        <div className="space-y-[12px]">
          {watch.technical_notes && (
            <div className="bg-zinc-900 border border-zinc-800 p-[24px]">
              <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-3">Note Tecniche</p>
              <p className="text-sm text-zinc-400 leading-relaxed">{watch.technical_notes}</p>
            </div>
          )}

          {sentiment && (
            <div className="bg-zinc-900 border border-zinc-800 p-[24px]">
              <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-3">Sentiment Aste Mondiali</p>
              <div className="space-y-2">
                {sentiment.total_lots && (
                  <SpecRow label="Lotti analizzati" value={sentiment.total_lots.toString()} />
                )}
                {sentiment.sell_through_rate && (
                  <SpecRow label="Sell-through rate" value={`${(sentiment.sell_through_rate * 100).toFixed(0)}%`} />
                )}
                {sentiment.avg_hammer_to_estimate_ratio && (
                  <SpecRow label="Rapporto martello/stima" value={`${(sentiment.avg_hammer_to_estimate_ratio * 100).toFixed(0)}%`} />
                )}
                {sentiment.price_trend_12m != null && (
                  <SpecRow
                    label="Trend 12 mesi"
                    value={`${sentiment.price_trend_12m > 0 ? '+' : ''}${(sentiment.price_trend_12m * 100).toFixed(1)}%`}
                    valueColor={sentiment.price_trend_12m >= 0 ? 'text-green-400' : 'text-red-400'}
                  />
                )}
              </div>
            </div>
          )}

          {/* Variants */}
          {watch.variants.length > 0 && (
            <div className="bg-zinc-900 border border-zinc-800 p-[24px]">
              <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-3">Varianti</p>
              <div className="flex flex-wrap gap-2">
                {watch.variants.map(v => (
                  <button
                    key={v.variant_reference}
                    onClick={() => navigate(`/encyclopedia/${encodeURIComponent(v.variant_reference)}`)}
                    className="font-mono-data text-mono-data text-yellow-400 bg-zinc-800 border border-zinc-700 px-3 py-1 rounded hover:border-yellow-400/40 transition-colors"
                  >
                    {v.variant_reference}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stories & Curiosities */}
      {watch.stories.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 p-[24px] mb-[12px]">
          <p className="font-label-caps text-label-caps text-zinc-400 uppercase mb-5">Storia & Curiosità</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {watch.stories.map(story => (
              <div key={story.id} className="bg-zinc-800/30 border border-zinc-700/40 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined text-sm text-yellow-400 leading-none">
                    {story.category === 'history' ? 'history' :
                     story.category === 'celebrity' ? 'star' :
                     story.category === 'auction_record' ? 'gavel' : 'info'}
                  </span>
                  {story.category && (
                    <span className="font-label-caps text-label-caps text-zinc-500 uppercase">
                      {story.category.replace('_', ' ')}
                    </span>
                  )}
                </div>
                <p className="font-['Space_Grotesk'] font-semibold text-zinc-100 text-sm mb-1">{story.title}</p>
                <p className="text-xs text-zinc-400 leading-relaxed">{story.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Auction Results */}
      {auctionData && auctionData.results.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 p-[24px]">
          <div className="flex items-center justify-between mb-5">
            <p className="font-label-caps text-label-caps text-zinc-400 uppercase">Risultati Aste Recenti</p>
            <span className="font-label-caps text-label-caps text-zinc-600 uppercase">{auctionData.total} lotti totali</span>
          </div>
          <div className="space-y-[4px]">
            {auctionData.results.map((result, i) => (
              <div key={result.id ?? i} className="flex items-center justify-between gap-4 bg-zinc-800/30 border border-zinc-700/40 px-[24px] py-3">
                <div className="flex items-center gap-4">
                  <div>
                    <p className="font-label-caps text-label-caps text-zinc-500 uppercase">{result.auction_house}</p>
                    <p className="text-xs text-zinc-400">{result.sale_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-zinc-600">{result.sale_date}</p>
                    <p className="text-xs text-zinc-600">{result.sale_location}</p>
                  </div>
                </div>
                <div className="text-right">
                  {result.total_price_chf && (
                    <p className="font-mono-data text-mono-data text-yellow-400">
                      CHF {result.total_price_chf.toLocaleString('it-IT')}
                    </p>
                  )}
                  {result.estimate_low_chf && result.estimate_high_chf && (
                    <p className="text-xs text-zinc-600">
                      Stima CHF {result.estimate_low_chf.toLocaleString('it-IT')} – {result.estimate_high_chf.toLocaleString('it-IT')}
                    </p>
                  )}
                  {result.is_record && (
                    <span className="font-label-caps text-label-caps text-yellow-400 bg-yellow-400/10 border border-yellow-400/20 px-2 py-0.5 rounded uppercase">
                      Record
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function SpecRow({ label, value, valueColor }: { label: string; value: string | null | undefined; valueColor?: string }) {
  if (!value) return null
  return (
    <div className="flex items-center justify-between gap-4 py-1.5 border-b border-zinc-800">
      <span className="font-label-caps text-label-caps text-zinc-500 uppercase">{label}</span>
      <span className={clsx('font-mono-data text-mono-data', valueColor ?? 'text-zinc-100')}>{value}</span>
    </div>
  )
}
