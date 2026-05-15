import { useState } from 'react'
import { useLang } from '../lib/lang'

export default function OptOutPage() {
  const { t } = useLang()

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [reason, setReason] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim()) return

    setStatus('loading')
    try {
      const res = await fetch('/api/opt-out', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username.trim(),
          email: email.trim() || undefined,
          reason: reason.trim() || undefined,
        }),
      })
      if (!res.ok) throw new Error('Request failed')
      setStatus('success')
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="min-h-full px-8 py-10 max-w-2xl mx-auto">

      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-outlined text-yellow-400 text-2xl">do_not_disturb_on</span>
          <span className="text-[10px] font-mono tracking-widest text-zinc-500 uppercase">Dealer Opt-Out</span>
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 font-['Space_Grotesk'] mb-3">
          {t.optOutTitle}
        </h1>
        <p className="text-sm text-zinc-400 leading-relaxed">
          {t.optOutSub}
        </p>
      </div>

      {/* Success state */}
      {status === 'success' ? (
        <div className="bg-zinc-900 border border-yellow-400/30 rounded-lg p-8 text-center">
          <span className="material-symbols-outlined text-yellow-400 text-4xl mb-4 block">check_circle</span>
          <p className="text-sm text-zinc-300 leading-relaxed">{t.optOutSuccess}</p>
        </div>
      ) : (
        /* Form */
        <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 space-y-6">

          {/* Username */}
          <div>
            <label className="block text-[11px] font-mono tracking-widest text-zinc-400 uppercase mb-2">
              {t.optOutUsernameLabel}
              <span className="text-yellow-400 ml-1">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 text-sm font-mono">@</span>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder={t.optOutUsernamePlaceholder}
                required
                className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm py-2.5 pl-8 pr-4 rounded focus:outline-none focus:border-yellow-400 transition-colors placeholder-zinc-600"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-[11px] font-mono tracking-widest text-zinc-400 uppercase mb-2">
              {t.optOutEmailLabel}
            </label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder={t.optOutEmailPlaceholder}
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm py-2.5 px-4 rounded focus:outline-none focus:border-yellow-400 transition-colors placeholder-zinc-600"
            />
          </div>

          {/* Reason */}
          <div>
            <label className="block text-[11px] font-mono tracking-widest text-zinc-400 uppercase mb-2">
              {t.optOutReasonLabel}
            </label>
            <textarea
              value={reason}
              onChange={e => setReason(e.target.value)}
              placeholder={t.optOutReasonPlaceholder}
              rows={4}
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm py-2.5 px-4 rounded focus:outline-none focus:border-yellow-400 transition-colors placeholder-zinc-600 resize-none"
            />
          </div>

          {/* Error message */}
          {status === 'error' && (
            <div className="flex items-center gap-2 text-red-400 text-xs">
              <span className="material-symbols-outlined text-base">error</span>
              {t.optOutError}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={status === 'loading' || !username.trim()}
            className="w-full py-3 bg-yellow-400 text-zinc-950 font-bold rounded text-xs uppercase tracking-widest transition-opacity hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {status === 'loading' ? t.optOutSubmitting : t.optOutSubmit}
          </button>
        </form>
      )}

      {/* Note */}
      <p className="mt-6 text-[11px] text-zinc-600 leading-relaxed">
        WatchScanner raccoglie dati pubblici disponibili su piattaforme social. L'opt-out viene elaborato entro 24 ore lavorative.
      </p>

    </div>
  )
}
