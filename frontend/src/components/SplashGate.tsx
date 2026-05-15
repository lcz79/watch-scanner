/**
 * SplashGate — Password gate + coming-soon page.
 * Password stored in localStorage so it persists across sessions.
 * To change the password update GATE_PASSWORD below.
 */

import { useState, useEffect, useRef } from 'react'

const GATE_PASSWORD = 'ws2026'
const STORAGE_KEY   = 'ws_gate_unlocked'

// Rolex Daytona Cosmograph ref. 16520 — Zenith era, white dial, dramatic smoke
const BG_IMAGE =
  'https://images.unsplash.com/photo-1657104996708-044ef9812f85?q=90&w=2200&auto=format&fit=crop'

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
  const [password, setPassword]       = useState('')
  const [pwError, setPwError]         = useState(false)
  const [shake, setShake]             = useState(false)
  const [visible, setVisible]         = useState(false)

  // Waitlist state
  const [email, setEmail]             = useState('')
  const [emailSent, setEmailSent]     = useState(false)
  const [emailLoading, setEmailLoading] = useState(false)
  const [emailError, setEmailError]   = useState('')

  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 60)
    return () => clearTimeout(t)
  }, [])

  // ── Password ──────────────────────────────────────────────────────────────
  const handlePassword = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (password.trim().toLowerCase() === GATE_PASSWORD) {
      setPwError(false)
      setTimeout(onUnlock, 280)
    } else {
      setPwError(true)
      setShake(true)
      setPassword('')
      setTimeout(() => setShake(false), 500)
      inputRef.current?.focus()
    }
  }

  // ── Waitlist ──────────────────────────────────────────────────────────────
  const handleWaitlist = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = email.trim().toLowerCase()
    if (!trimmed || !trimmed.includes('@') || !trimmed.split('@')[1]?.includes('.')) {
      setEmailError('Inserisci un indirizzo email valido.')
      return
    }
    setEmailLoading(true)
    setEmailError('')
    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmed }),
      })
      if (res.ok) {
        setEmailSent(true)
      } else {
        setEmailError('Errore. Riprova tra poco.')
      }
    } catch {
      setEmailError('Errore di rete. Riprova.')
    } finally {
      setEmailLoading(false)
    }
  }

  return (
    <div
      className={`fixed inset-0 z-50 flex transition-opacity duration-700 ${visible ? 'opacity-100' : 'opacity-0'}`}
    >
      {/* ── Left: emotional image ─────────────────────────────────────────── */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden">
        <img
          src={BG_IMAGE}
          alt="Rolex Daytona 16520"
          className="absolute inset-0 w-full h-full object-cover scale-[1.04]"
          style={{ filter: 'brightness(0.65) saturate(0.85)' }}
        />
        {/* Vignette + right-fade */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/10 via-black/5 to-zinc-950/95" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-black/20" />

        {/* Caption bottom-left */}
        <div className="absolute bottom-10 left-10 max-w-[280px]">
          <p className="text-zinc-200 text-xl font-light leading-snug italic mb-3">
            "Il mercato non dorme.<br />Il tuo vantaggio neanche."
          </p>
          <div className="w-10 h-px bg-yellow-400 mb-3" />
          <p className="text-zinc-500 text-[11px] uppercase tracking-widest">
            Rolex Cosmograph Daytona — Ref. 16520
          </p>
        </div>

        {/* Corner marks */}
        <div className="absolute top-8 left-8 w-10 h-10 border-t-2 border-l-2 border-yellow-400/25" />
        <div className="absolute bottom-8 right-12 w-10 h-10 border-b-2 border-r-2 border-yellow-400/25" />
      </div>

      {/* ── Right: brand + content ────────────────────────────────────────── */}
      <div className="w-full lg:w-[500px] flex-shrink-0 bg-zinc-950 flex flex-col relative overflow-y-auto">

        {/* Mobile BG */}
        <div className="lg:hidden absolute inset-0 overflow-hidden pointer-events-none">
          <img src={BG_IMAGE} alt="" className="w-full h-full object-cover"
            style={{ filter: 'brightness(0.18) saturate(0.6)' }} />
          <div className="absolute inset-0 bg-zinc-950/75" />
        </div>

        <div className="relative flex flex-col min-h-full px-10 py-12 gap-0">

          {/* Logo */}
          <div className="flex items-center gap-2.5 mb-1">
            <div className="w-7 h-7 border border-yellow-400 flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-yellow-400 text-sm leading-none"
                style={{ fontVariationSettings: "'FILL' 1" }}>watch</span>
            </div>
            <span className="font-['Cabinet_Grotesk'] font-black text-base tracking-tight text-zinc-100 uppercase">
              WatchScanner
            </span>
          </div>
          <p className="text-[9px] text-zinc-600 uppercase tracking-[0.18em] ml-[38px] mb-12">
            Market Intelligence Platform
          </p>

          {/* Headline */}
          <div className="mb-8">
            <p className="text-[10px] text-yellow-400 uppercase tracking-[0.22em] mb-4 font-medium">
              Coming Soon
            </p>
            <h1 className="font-['Cabinet_Grotesk'] font-black text-[2.4rem] leading-[1.04] text-zinc-100 mb-5">
              Il motore di<br />
              intelligence per<br />
              <span className="text-yellow-400">l'orologeria</span><br />
              di lusso.
            </h1>
            <p className="text-zinc-400 text-sm leading-relaxed">
              WatchScanner aggrega e analizza in tempo reale i dati di prezzo
              provenienti da <span className="text-zinc-300">marketplace mondiali,
              social, siti web di reseller e case d'asta</span> — per trovare
              il prezzo minimo su ogni referenza e segnalarti le opportunità
              prima che scompaiano.
            </p>
          </div>

          {/* Feature bullets */}
          <div className="space-y-2.5 mb-10">
            {[
              { icon: 'radar',               label: 'Monitoraggio real-time su marketplace mondiali, social e aste' },
              { icon: 'trending_down',       label: 'Rilevamento automatico del prezzo minimo di mercato' },
              { icon: 'notifications_active',label: 'Alert istantanei quando il mercato si muove' },
              { icon: 'gavel',               label: 'Database storico delle principali case d\'asta internazionali' },
            ].map(f => (
              <div key={f.icon} className="flex items-start gap-3">
                <span className="material-symbols-outlined text-yellow-400 text-[15px] leading-none mt-0.5 flex-shrink-0"
                  style={{ fontVariationSettings: "'FILL' 1" }}>{f.icon}</span>
                <span className="text-zinc-400 text-xs leading-relaxed">{f.label}</span>
              </div>
            ))}
          </div>

          {/* ── Waitlist ─────────────────────────────────────────────────── */}
          <div className="border border-zinc-800 bg-zinc-900/50 p-5 mb-8">
            {emailSent ? (
              <div className="flex items-center gap-3 py-1">
                <span className="material-symbols-outlined text-green-400 text-xl leading-none"
                  style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                <div>
                  <p className="text-zinc-200 text-sm font-medium">Sei nella lista!</p>
                  <p className="text-zinc-500 text-xs mt-0.5">
                    Ti avviseremo non appena WatchScanner sarà disponibile al pubblico.
                  </p>
                </div>
              </div>
            ) : (
              <>
                <p className="text-zinc-300 text-xs font-medium mb-0.5">
                  Vuoi essere tra i primi a provarlo?
                </p>
                <p className="text-zinc-600 text-[11px] mb-4">
                  Lascia la tua email — ti avvisiamo al lancio.
                </p>
                <form onSubmit={handleWaitlist} className="flex gap-2">
                  <div className="flex-1 relative">
                    <input
                      type="email"
                      value={email}
                      onChange={e => { setEmail(e.target.value); setEmailError('') }}
                      placeholder="la@tua.email"
                      className={`w-full bg-zinc-950 border text-sm py-2.5 px-3 text-zinc-200 placeholder-zinc-700 focus:outline-none transition-colors ${
                        emailError ? 'border-red-500' : 'border-zinc-800 focus:border-yellow-400/60'
                      }`}
                    />
                    {emailError && (
                      <p className="absolute -bottom-4 left-0 text-[10px] text-red-400">{emailError}</p>
                    )}
                  </div>
                  <button
                    type="submit"
                    disabled={emailLoading}
                    className="px-4 py-2.5 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-[11px] font-bold uppercase tracking-widest transition-colors flex-shrink-0 disabled:opacity-50"
                  >
                    {emailLoading ? '…' : 'Notificami'}
                  </button>
                </form>
              </>
            )}
          </div>

          {/* ── Password ─────────────────────────────────────────────────── */}
          <div className="mt-auto">
            <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-3">
              Accesso privato
            </p>
            <form onSubmit={handlePassword}
              className={shake ? 'animate-[shake_0.42s_ease]' : ''}>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="password"
                    value={password}
                    onChange={e => { setPassword(e.target.value); setPwError(false) }}
                    placeholder="Password"
                    autoFocus
                    className={`w-full bg-zinc-900 border text-sm py-3 px-4 text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors ${
                      pwError ? 'border-red-500' : 'border-zinc-800 focus:border-yellow-400'
                    }`}
                  />
                  {pwError && (
                    <p className="absolute -bottom-5 left-0 text-[10px] text-red-400">
                      Password errata. Riprova.
                    </p>
                  )}
                </div>
                <button type="submit"
                  className="px-5 py-3 bg-yellow-400 hover:bg-yellow-300 text-zinc-950 text-xs font-black uppercase tracking-widest transition-colors flex-shrink-0 flex items-center gap-1.5">
                  Entra
                  <span className="material-symbols-outlined text-sm leading-none">arrow_forward</span>
                </button>
              </div>
            </form>
          </div>

          {/* Footer */}
          <div className="mt-10 pt-5 border-t border-zinc-900">
            <p className="text-[10px] text-zinc-700">
              watchscanner.it © 2026 — Piattaforma privata, accesso su invito
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes shake {
          0%,100% { transform: translateX(0) }
          20%     { transform: translateX(-8px) }
          40%     { transform: translateX(8px) }
          60%     { transform: translateX(-5px) }
          80%     { transform: translateX(5px) }
        }
      `}</style>
    </div>
  )
}
