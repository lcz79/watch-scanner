import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAlerts, createAlert, deleteAlert } from '../lib/api'
import type { AlertConfig } from '../types'
import { formatDistanceToNow } from 'date-fns'
import { it as itLocale, enUS } from 'date-fns/locale'
import { useLang } from '../lib/lang'

export default function AlertsPage() {
  const qc = useQueryClient()
  const { t, lang } = useLang()
  const [form, setForm] = useState<AlertConfig>({ reference: '', max_price: 0 })

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: getAlerts,
  })

  const create = useMutation({
    mutationFn: createAlert,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['alerts'] })
      setForm({ reference: '', max_price: 0 })
    },
  })

  const remove = useMutation({
    mutationFn: deleteAlert,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }),
  })

  return (
    <div className="p-8 max-w-[1600px] mx-auto">

      {/* Header */}
      <div className="mb-10 flex items-end justify-between">
        <div>
          <span className="font-label-caps text-primary uppercase text-[10px] tracking-[0.2em] mb-2 block">{t.surveillanceLabel}</span>
          <h2 className="font-h1 text-on-surface text-3xl">{t.alertsTitle}</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-2 rounded">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="font-mono-data text-[11px] text-zinc-400 uppercase tracking-tighter">{t.monitoringOnline}</span>
          </div>
          <div className="text-right">
            <p className="font-mono-data text-[10px] text-zinc-500 uppercase">{t.totalScanned}</p>
            <p className="font-mono-data text-sm text-zinc-200">{t.listingsDay}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8">

        {/* Left column: Create form + volatility */}
        <div className="col-span-12 lg:col-span-4 space-y-6">

          <section className="bg-zinc-900 border border-zinc-800 p-6 shadow-2xl">
            <div className="flex items-center gap-3 mb-6">
              <span className="material-symbols-outlined text-primary">add_circle</span>
              <h3 className="font-h2 text-lg uppercase tracking-tight">{t.createSurveillance}</h3>
            </div>
            <div className="space-y-6">
              <div>
                <label className="block font-label-caps text-[10px] text-zinc-500 uppercase mb-2">{t.watchReferenceLabel}</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-zinc-600 text-sm">search</span>
                  <input
                    className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm pl-10 py-2.5 px-3 focus:border-primary focus:outline-none transition-all rounded"
                    placeholder={t.watchReferencePlaceholder}
                    type="text"
                    value={form.reference}
                    onChange={e => setForm(f => ({ ...f, reference: e.target.value.toUpperCase() }))}
                  />
                </div>
              </div>

              <div>
                <label className="block font-label-caps text-[10px] text-zinc-500 uppercase mb-2">{t.targetPriceLabel}</label>
                <input
                  className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm py-2.5 px-3 focus:border-primary focus:outline-none transition-all font-mono-data rounded"
                  placeholder={t.targetPricePlaceholder}
                  type="number"
                  value={form.max_price || ''}
                  onChange={e => setForm(f => ({ ...f, max_price: parseFloat(e.target.value) }))}
                />
                <p className="mt-1 text-[10px] text-zinc-600 italic">{t.targetPriceSub}</p>
              </div>

              <div>
                <label className="block font-label-caps text-[10px] text-zinc-500 uppercase mb-2">{t.emailNotification}</label>
                <input
                  className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm py-2.5 px-3 focus:border-primary focus:outline-none transition-all rounded"
                  placeholder="your@email.com"
                  type="email"
                  value={form.notify_email || ''}
                  onChange={e => setForm(f => ({ ...f, notify_email: e.target.value }))}
                />
              </div>

              <div>
                <label className="block font-label-caps text-[10px] text-zinc-500 uppercase mb-4">{t.notificationChannels}</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { icon: 'mail', label: 'Email' },
                    { icon: 'send', label: 'Telegram' },
                    { icon: 'chat', label: 'WhatsApp' },
                  ].map(ch => (
                    <label key={ch.label} className="flex flex-col items-center justify-center p-3 border border-zinc-800 rounded bg-zinc-950 hover:border-primary cursor-pointer transition-colors group">
                      <input type="checkbox" className="hidden" />
                      <span className="material-symbols-outlined text-zinc-600 group-hover:text-primary transition-colors mb-1">{ch.icon}</span>
                      <span className="text-[9px] font-label-caps text-zinc-500 uppercase">{ch.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block font-label-caps text-[10px] text-zinc-500 uppercase mb-3">{t.scanningSources}</label>
                <div className="space-y-2">
                  {[
                    { label: 'Chrono24 Global', locked: false },
                    { label: 'eBay Marketplace', locked: false },
                    { label: 'Premium Private Dealers', locked: true },
                  ].map(src => (
                    <div key={src.label} className="flex items-center justify-between text-xs px-3 py-2 bg-zinc-950 border border-zinc-800 rounded">
                      <span className={src.locked ? 'text-zinc-300 italic' : 'text-zinc-400'}>{src.label}</span>
                      {src.locked
                        ? <span className="material-symbols-outlined text-zinc-700 text-sm">lock</span>
                        : <div className="w-4 h-4 bg-primary text-on-primary rounded-sm flex items-center justify-center"><span className="material-symbols-outlined text-[10px]">check</span></div>
                      }
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => create.mutate(form)}
                disabled={create.isPending || !form.reference || !form.max_price}
                className="w-full bg-primary text-on-primary py-3 font-label-caps text-xs tracking-widest rounded hover:brightness-110 transition-all uppercase shadow-lg shadow-primary/10 disabled:opacity-50"
              >
                {create.isPending ? t.initializingAlert : t.initializeAlert}
              </button>
            </div>
          </section>

          {/* Market Volatility */}
          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded relative overflow-hidden group">
            <div className="relative z-10">
              <h4 className="font-h2 text-sm text-zinc-400 mb-2">{t.marketVolatility}</h4>
              <p className="font-display-price text-3xl text-primary">{t.volatilityIndex}</p>
              <p className="text-[10px] font-mono-data text-green-400 mt-2 uppercase">{t.stableBuying}</p>
            </div>
            <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-9xl">trending_up</span>
            </div>
          </div>
        </div>

        {/* Right column: active alerts */}
        <div className="col-span-12 lg:col-span-8 space-y-6">

          <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
            <h3 className="font-label-caps text-xs text-zinc-500 uppercase">
              {t.activeMonitored} ({isLoading ? '…' : (alerts?.length ?? 0).toString().padStart(2, '0')})
            </h3>
            <div className="flex gap-2">
              <button className="p-1.5 bg-zinc-800 border border-zinc-700 rounded text-zinc-400 hover:text-primary">
                <span className="material-symbols-outlined text-sm">filter_list</span>
              </button>
              <button className="p-1.5 bg-zinc-800 border border-zinc-700 rounded text-zinc-400 hover:text-primary">
                <span className="material-symbols-outlined text-sm">sort</span>
              </button>
            </div>
          </div>

          {isLoading && (
            <div className="bg-zinc-900 border border-zinc-800 p-6 animate-pulse h-32" />
          )}

          {!isLoading && alerts?.map(alert => (
            <article
              key={alert.alert_id}
              className="bg-zinc-900 border border-zinc-800 p-6 hover:border-primary/50 transition-colors flex flex-col md:flex-row gap-6"
            >
              {/* Image placeholder */}
              <div className="w-full md:w-32 h-32 bg-zinc-950 border border-zinc-800 flex-shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-4xl text-zinc-700">watch</span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-mono-data text-[10px] text-zinc-500 uppercase mb-1">{t.ref} {alert.config.reference}</p>
                    <h4 className="font-h2 text-lg text-zinc-100 truncate">{alert.config.reference}</h4>
                  </div>
                  <div className="text-right">
                    {alert.last_triggered ? (
                      <span className="bg-green-500/10 text-green-400 px-2 py-1 rounded text-[10px] font-label-caps uppercase border border-green-500/20">{t.targetHit}</span>
                    ) : (
                      <span className="bg-primary/10 text-primary px-2 py-1 rounded text-[10px] font-label-caps uppercase border border-primary/20">{t.scanning}</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6 mt-4">
                  <div>
                    <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">{t.targetPrice}</p>
                    <p className="font-mono-data text-zinc-100">{alert.config.max_price.toLocaleString(lang === 'it' ? 'it-IT' : 'en-US')} €</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-label-caps text-zinc-500 uppercase mb-1">
                      {alert.last_triggered ? t.lastTriggered : t.checkEvery}
                    </p>
                    <p className="font-mono-data text-zinc-400 text-sm">
                      {alert.last_triggered
                        ? formatDistanceToNow(new Date(alert.last_triggered), { addSuffix: true, locale: lang === 'it' ? itLocale : enUS })
                        : t.every30min
                      }
                    </p>
                  </div>
                </div>

                {alert.config.notify_email && (
                  <p className="text-[10px] text-zinc-500 mt-3 flex items-center gap-1 uppercase tracking-widest">
                    <span className="material-symbols-outlined text-sm leading-none">mail</span>
                    {alert.config.notify_email}
                  </p>
                )}
              </div>

              <div className="flex md:flex-col justify-end gap-2 border-l border-zinc-800 pl-6">
                <button className="p-2 hover:bg-zinc-800 rounded transition-colors text-zinc-500 hover:text-zinc-100">
                  <span className="material-symbols-outlined text-lg">notifications_off</span>
                </button>
                <button
                  onClick={() => remove.mutate(alert.alert_id)}
                  className="p-2 hover:bg-zinc-800 rounded transition-colors text-red-500/70 hover:text-red-500"
                >
                  <span className="material-symbols-outlined text-lg">delete</span>
                </button>
              </div>
            </article>
          ))}

          {/* Empty slot placeholders */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-950 border border-zinc-800 border-dashed p-8 flex flex-col items-center justify-center text-center opacity-60">
              <span className="material-symbols-outlined text-3xl text-zinc-700 mb-3">add_alarm</span>
              <p className="font-label-caps text-[10px] text-zinc-500 uppercase">{t.slotAvailable}</p>
            </div>
            <div className="bg-zinc-950 border border-zinc-800 border-dashed p-8 flex flex-col items-center justify-center text-center opacity-60">
              <span className="material-symbols-outlined text-3xl text-zinc-700 mb-3">lock</span>
              <p className="font-label-caps text-[10px] text-zinc-500 uppercase">{t.upgradeMore}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer stats */}
      <footer className="mt-12 pt-8 border-t border-zinc-800 grid grid-cols-4 gap-8">
        <div className="space-y-1">
          <p className="text-[10px] font-label-caps text-zinc-500 uppercase">{t.scanFrequency}</p>
          <p className="font-mono-data text-sm text-zinc-300">{t.every30min}</p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] font-label-caps text-zinc-500 uppercase">{t.avgResponse}</p>
          <p className="font-mono-data text-sm text-zinc-300">{t.responseTime}</p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] font-label-caps text-zinc-500 uppercase">{t.alertEfficiency}</p>
          <p className="font-mono-data text-sm text-green-400">{t.accuracy}</p>
        </div>
        <div className="flex justify-end items-center">
          <div className="flex -space-x-2">
            {['E', 'T', 'W'].map(ch => (
              <div key={ch} className="w-6 h-6 rounded-full border border-zinc-900 bg-zinc-800 flex items-center justify-center">
                <span className="text-[8px]">{ch}</span>
              </div>
            ))}
          </div>
          <span className="ml-3 text-[10px] font-label-caps text-zinc-600 uppercase">{t.activeChannels}</span>
        </div>
      </footer>

    </div>
  )
}
