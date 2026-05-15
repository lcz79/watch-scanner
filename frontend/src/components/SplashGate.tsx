/**
 * SplashGate — Password gate + coming-soon page.
 * Shown to all visitors until the correct password is entered.
 * Password is stored in localStorage so it persists across sessions.
 *
 * To change the password, update GATE_PASSWORD below.
 */

import { useState, useEffect, useRef } from 'react'

const GATE_PASSWORD = 'ws2026'
const STORAGE_KEY   = 'ws_gate_unlocked'

// Unsplash: dramatic macro of a luxury watch dial
const BG_IMAGE =
  'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?q=85&w=2000&auto=format&fit=crop'

export function useSplashGate() {
  const [unlocked, setUnlocked] = useState(() => {
    try { return localStorage.getItem(STORAGE_KEY) === '1' } catch { return false }
  })
  const unlock = () => {
    try { localStorage.setItem(STORAGE_KEY, '1') } catch {}
    setUnlocked(true)
  }
  return { unlocked, unlock }
}

export default function SplashGate({ onUnlock }: { onUnlock: () => void }) {
  const [password, setPassword]   = useState('')
  const [error, setError]         = useState(false)
  const [shake, setShake]         = useState(false)
  const [visible, setVisible]     = useState(false)
  const inputRef                  = useRef<HTMLInputElement>(null)

  // Fade-in on mount
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 60)
    return () => clearTimeout(t)
  }, [])

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (password.trim().toLowerCase() === GATE_PASSWORD) {
      setError(false)
      // Brief pause before unlocking so the success state is visible
      setTimeout(onUnlock, 300)
    } else {
      setError(true)
      setShake(true)
      setPassword('')
      setTimeout(() => setShake(false), 500)
      inputRef.current?.focus()
    }
  }

  return (
    <div
      className={`fixed inset-0 z-50 flex transition-opacity duration-700 ${visible ? 'opacity-100' : 'opacity-0'}`}
      style={{ fontFamily: 'inherit' }}
    >
      {/* ── Left panel: emotional image ── */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden">
        {/* Photo */}
        <img
          src={BG_IMAGE}
          alt="Luxury watch"
          className="absolute inset-0 w-full h-full object-cover grayscale scale-105"
          style={{ filter: 'grayscale(0.6) brightness(0.45)' }}
        />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-zinc-950/20 via-zinc-950/10 to-zinc-950/90" />
        <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/60 via-transparent to-zinc-950/30" />

        {/* Quote bottom-left */}
        <div className="absolute bottom-12 left-12 max-w-xs">
          <p className="text-zinc-300 text-lg font-light leading-snug italic mb-3">
            "Il mercato non dorme.<br />Il tuo vantaggio neanche."
          </p>
          <div className="w-8 h-px bg-yellow-400" />
        </div>

        {/* Decorative corner lines */}
        <div className="absolute top-8 left-8 w-12 h-12 border-t border-l border-yellow-400/30" />
        <div className="absolute bottom-8 right-8 w-12 h-12 border-b border-r border-yellow-400/30" />
      </div>

      {/* ── Right panel: brand + password ── */}
      <div className="w-full lg:w-[520px] flex-shrink-0 bg-zinc-950 flex flex-col relative overflow-y-auto">

        {/* Mobile background */}
        <div className="lg:hidden absolute inset-0 overflow-hidden">
          <img
            src={BG_IMAGE}
            alt=""
            className="w-full h-full object-cover"
            style={{ filter: 'grayscale(0.7) brightness(0.25)' }}
          />
          <div className="absolute inset-0 bg-zinc-950/80" />
        </div>

        <div className="relative flex flex-col h-full px-10 py-12">

          {/* Logo */}
          <div className="mb-auto">
            <div className="flex items-center gap-3 mb-1">
              <div className="w-7 h-7 border border-yellow-400 flex items-center justify-center">
                <span className="material-symbols-outlined text-yellow-400 text-sm leading-none"
                  style={{ fontVariationSettings: "'FILL' 1" }}>
                  watch
                </span>
              </div>
              <span className="font-['Cabinet_Grotesk'] font-black text-lg tracking-tight text-zinc-100 uppercase">
                WatchScanner
              </span>
            </div>
            <p className="text-[10px] text-zinc-600 uppercase tracking-widest ml-10">
              Market Intelligence Platform
            </p>
          </div>

          {/* Hero text */}
          <div className="mt-16 mb-10">
            <p className="font-label-caps text-[10px] text-yellow-400 uppercase tracking-[0.2em] mb-4">
              Coming Soon
            </p>
            <h1 className="font-['Cabinet_Grotesk'] font-black text-4xl leading-[1.05] text-zinc-100 mb-6">
              Il motore di<br />
              intelligence per<br />
              <span className="text-yellow-400">l'orologeria</span><br />
              di lusso.
            </h1>
            <p className="text-zinc-400 text-sm leading-relaxed max-w-sm">
              WatchScanner scansiona in tempo reale Chrono24, eBay, Instagram e le
              principali case d'asta mondiali per trovare il prezzo minimo su ogni referenza
              e segnalarti le opportunità prima che scompaiano.
            </p>
          </div>

          {/* Features */}
          <div className="space-y-3 mb-10">
            {[
              { icon: 'radar',         text: 'Scansione real-time su 5+ fonti di mercato' },
              { icon: 'trending_down', text: 'Rilevamento automatico del prezzo minimo' },
              { icon: 'notifications_active', text: 'Alert istantanei quando il mercato si muove' },
              { icon: 'gavel',         text: 'Storico prezzi da Christie\'s, Phillips, Sotheby\'s' },
            ].map(f => (
              <div key={f.icon} className="flex items-center gap-3">
                <span className="material-symbols-outlined text-yellow-400 text-base leading-none flex-shrink-0"
                  style={{ fontVariationSettings: "'FILL' 1" }}>
                  {f.icon}
                </span>
                <span className="text-zinc-400 text-xs">{f.text}</span>
              </div>
            ))}
          </div>

          {/* Password form */}
          <div className="mt-auto">
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest mb-3">
              Accesso privato
            </p>
            <form onSubmit={handleSubmit} className={shake ? 'animate-[shake_0.4s_ease]' : ''}>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="password"
                    value={password}
                    onChange={e => { setPassword(e.target.value); setError(false) }}
                    placeholder="Password"
                    autoFocus
                    className={`w-full bg-zinc-900 border text-sm py-3 px-4 text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors ${
                      error
                        ? 'border-red-500 focus:border-red-400'
                        : 'border-zinc-800 focus:border-yellow-400'
                    }`}
                  />
                  {error && (
                    <p className="absolute -bottom-5 left-0 text-[10px] text-red-400">
                      Password errata. Riprova.
                    </p>
                  )}
                </div>
                <button
                  type="submit"
                  className="px-5 py-3 bg-yellow-400 hover:bg-yellow-300 text-zinc-950 text-xs font-black uppercase tracking-widest transition-colors flex-shrink-0 flex items-center gap-1.5"
                >
                  Entra
                  <span className="material-symbols-outlined text-sm leading-none">arrow_forward</span>
                </button>
              </div>
            </form>
          </div>

          {/* Footer */}
          <div className="mt-10 pt-6 border-t border-zinc-900">
            <p className="text-[10px] text-zinc-700">
              watchscanner.it © 2026 — Piattaforma privata, accesso su invito
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0) }
          20%       { transform: translateX(-8px) }
          40%       { transform: translateX(8px) }
          60%       { transform: translateX(-6px) }
          80%       { transform: translateX(6px) }
        }
      `}</style>
    </div>
  )
}
