import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAlerts, createAlert, deleteAlert } from '../lib/api'
import { Bell, Plus, Trash2, Loader2, Mail, Clock } from 'lucide-react'
import type { AlertConfig } from '../types'
import { formatDistanceToNow } from 'date-fns'
import { it } from 'date-fns/locale'

export default function AlertsPage() {
  const qc = useQueryClient()
  const [form, setForm] = useState<AlertConfig>({ reference: '', max_price: 0 })
  const [showForm, setShowForm] = useState(false)

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: getAlerts,
  })

  const create = useMutation({
    mutationFn: createAlert,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['alerts'] })
      setShowForm(false)
      setForm({ reference: '', max_price: 0 })
    },
  })

  const remove = useMutation({
    mutationFn: deleteAlert,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }),
  })

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display font-bold text-3xl text-zinc-100 mb-1">Alert</h1>
          <p className="text-zinc-500">Ricevi una email quando un orologio scende sotto il tuo prezzo</p>
        </div>
        <button
          onClick={() => setShowForm(v => !v)}
          className="flex items-center gap-2 bg-gold-400 text-zinc-900 font-semibold px-4 py-2.5 rounded-xl hover:bg-gold-500 transition-colors text-sm"
        >
          <Plus size={16} /> Nuovo alert
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-zinc-900 border border-gold-400/30 rounded-2xl p-6 mb-6">
          <h3 className="font-semibold text-zinc-100 mb-4">Crea alert</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs text-zinc-500 mb-1.5 block">Referenza</label>
              <input
                value={form.reference}
                onChange={e => setForm(f => ({ ...f, reference: e.target.value.toUpperCase() }))}
                placeholder="es. 116610LN"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-2.5 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-gold-400 text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-zinc-500 mb-1.5 block">Prezzo massimo (€)</label>
              <input
                type="number"
                value={form.max_price || ''}
                onChange={e => setForm(f => ({ ...f, max_price: parseFloat(e.target.value) }))}
                placeholder="es. 14000"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-2.5 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-gold-400 text-sm"
              />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-zinc-500 mb-1.5 block">
                <Mail size={11} className="inline mr-1" />
                Email per le notifiche
              </label>
              <input
                type="email"
                value={form.notify_email || ''}
                onChange={e => setForm(f => ({ ...f, notify_email: e.target.value }))}
                placeholder="es. tuanome@gmail.com"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-2.5 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-gold-400 text-sm"
              />
              <p className="text-xs text-zinc-600 mt-1">Ti mandiamo un'email quando troviamo un'offerta sotto il prezzo indicato</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => create.mutate(form)}
              disabled={create.isPending || !form.reference || !form.max_price}
              className="flex items-center gap-2 bg-gold-400 text-zinc-900 font-semibold px-5 py-2.5 rounded-xl hover:bg-gold-500 disabled:opacity-50 text-sm transition-colors"
            >
              {create.isPending ? <Loader2 size={14} className="animate-spin" /> : <Bell size={14} />}
              Salva alert
            </button>
            <button onClick={() => setShowForm(false)} className="px-5 py-2.5 text-zinc-400 hover:text-zinc-100 text-sm transition-colors">
              Annulla
            </button>
          </div>
        </div>
      )}

      {/* List */}
      {isLoading && <div className="skeleton rounded-xl h-24" />}

      {!isLoading && (!alerts || alerts.length === 0) && (
        <div className="text-center py-20 text-zinc-600">
          <Bell size={40} className="mx-auto mb-4 opacity-30" />
          <p className="text-sm">Nessun alert configurato</p>
          <p className="text-xs mt-1">Crea il tuo primo alert con il pulsante in alto</p>
        </div>
      )}

      <div className="space-y-3">
        {alerts?.map(alert => (
          <div key={alert.alert_id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <span className="font-semibold text-zinc-100 font-display text-lg">{alert.config.reference}</span>
                <span className="text-xs text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 rounded-full px-2 py-0.5">
                  ● Attivo
                </span>
              </div>
              <p className="text-sm text-zinc-500">
                Avvisami sotto <span className="text-gold-400 font-semibold">{alert.config.max_price.toLocaleString('it-IT')} €</span>
              </p>
              {alert.config.notify_email && (
                <p className="text-xs text-zinc-600 mt-0.5 flex items-center gap-1">
                  <Mail size={10} />{alert.config.notify_email}
                </p>
              )}
              {alert.last_triggered && (
                <p className="text-xs text-zinc-600 mt-1 flex items-center gap-1">
                  <Clock size={10} />
                  Ultima notifica {formatDistanceToNow(new Date(alert.last_triggered), { addSuffix: true, locale: it })}
                </p>
              )}
              {!alert.last_triggered && (
                <p className="text-xs text-zinc-700 mt-1">Nessuna notifica ancora — controllo ogni 30 min</p>
              )}
            </div>
            <button
              onClick={() => remove.mutate(alert.alert_id)}
              className="text-zinc-600 hover:text-red-400 transition-colors p-2 rounded-lg hover:bg-red-400/10"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
