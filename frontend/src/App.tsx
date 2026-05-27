import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import Sidebar from './components/Sidebar'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import AgentsPage from './pages/AgentsPage'
import AlertsPage from './pages/AlertsPage'
import AuctionsPage from './pages/AuctionsPage'
import CatalogPage from './pages/CatalogPage'
import EncyclopediaDetailPage from './pages/EncyclopediaDetailPage'
import VerificationPage from './pages/VerificationPage'
import OptOutPage from './pages/OptOutPage'
import SplashGate, { useSplashGate } from './components/SplashGate'
import { useLang } from './lib/lang'

/* ── Ticker ──────────────────────────────────────────────────────────── */
const TICKER_ITEMS = [
  { ref: '5726/1A',    price: '€ 51.400', delta: '+34.2%', up: true  },
  { ref: '116610LN',  price: '€ 12.800', delta: '+2.1%',  up: true  },
  { ref: '6239',       price: '€ 890.000',delta: '-0.8%',  up: false },
  { ref: '5711/1A',   price: '€ 68.000', delta: '+12.7%', up: true  },
  { ref: '126710BLNR',price: '€ 15.900', delta: '-1.2%',  up: false },
  { ref: 'A13312',    price: '€ 4.800',  delta: '+8.9%',  up: true  },
  { ref: 'IW500401',  price: '€ 9.100',  delta: '+1.5%',  up: true  },
  { ref: '5167A',     price: '€ 22.300', delta: '+7.3%',  up: true  },
  { ref: 'RM 011',    price: '€ 195.000',delta: '+5.2%',  up: true  },
]

function Ticker() {
  const items = [...TICKER_ITEMS, ...TICKER_ITEMS] // duplicate for seamless loop
  return (
    <div
      style={{
        height: 28,
        background: '#060810',
        borderBottom: '1px solid rgba(184,151,90,0.12)',
        display: 'flex',
        alignItems: 'center',
        overflow: 'hidden',
        flexShrink: 0,
      }}
    >
      <div
        style={{
          background: '#B8975A',
          height: '100%',
          padding: '0 14px',
          display: 'flex',
          alignItems: 'center',
          flexShrink: 0,
          fontFamily: '"IBM Plex Mono", monospace',
          fontSize: 8,
          fontWeight: 700,
          letterSpacing: '0.18em',
          color: '#000',
          whiteSpace: 'nowrap',
        }}
      >
        LIVE
      </div>
      <div style={{ overflow: 'hidden', flex: 1, display: 'flex', alignItems: 'center' }}>
        <div
          style={{
            display: 'flex',
            gap: 40,
            padding: '0 24px',
            whiteSpace: 'nowrap',
            animation: 'wsTickerScroll 40s linear infinite',
          }}
        >
          {items.map((item, i) => (
            <span
              key={i}
              style={{ display: 'flex', alignItems: 'center', gap: 8, fontFamily: '"IBM Plex Mono", monospace', fontSize: 10 }}
            >
              <span style={{ color: '#B8975A', fontWeight: 600 }}>{item.ref}</span>
              <span style={{ color: '#8a8070' }}>·</span>
              <span style={{ color: '#e8e2d4' }}>{item.price}</span>
              <span style={{ color: item.up ? '#4EB87A' : '#E05A5A' }}>
                {item.up ? '▲' : '▼'} {item.delta}
              </span>
            </span>
          ))}
        </div>
      </div>
      <style>{`
        @keyframes wsTickerScroll {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  )
}

/* ── TopBar ──────────────────────────────────────────────────────────── */
function LiveClock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const update = () => {
      const now = new Date()
      const h = String(now.getHours()).padStart(2, '0')
      const m = String(now.getMinutes()).padStart(2, '0')
      const s = String(now.getSeconds()).padStart(2, '0')
      setTime(`${h}:${m}:${s}`)
    }
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])
  return (
    <div style={{ fontFamily: '"IBM Plex Mono", monospace', lineHeight: 1, textAlign: 'right' }}>
      <div style={{ fontSize: 13, fontWeight: 500, color: '#e8e2d4' }}>{time}</div>
      <div style={{ fontSize: 8, color: '#3d3a30', letterSpacing: '0.08em', marginTop: 2 }}>
        {new Date().toLocaleDateString('it-IT', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()}
      </div>
    </div>
  )
}

function TopBar() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const { lang, setLang } = useLang()

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && query.trim()) {
      navigate(`/search?ref=${encodeURIComponent(query.trim())}`)
      setQuery('')
    }
  }

  return (
    <header
      style={{
        height: 48,
        background: '#0c0e1a',
        borderBottom: '1px solid rgba(184,151,90,0.12)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 0 0 16px',
        flexShrink: 0,
        zIndex: 40,
      }}
    >
      {/* Search */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#111425', border: '1px solid rgba(184,151,90,0.12)', padding: '0 14px', height: 30 }}>
        <span className="material-symbols-outlined" style={{ fontSize: 14, color: '#3d3a30' }}>search</span>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleSearch}
          placeholder="Cerca referenza, marca..."
          style={{
            background: 'none', border: 'none', outline: 'none',
            fontFamily: '"IBM Plex Mono", monospace', fontSize: 11,
            color: '#e8e2d4', width: 220,
          }}
        />
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        <LiveClock />

        {/* Lang toggle */}
        <div style={{ display: 'flex', height: 48, borderLeft: '1px solid rgba(184,151,90,0.12)', marginLeft: 16 }}>
          {(['it', 'en'] as const).map(l => (
            <button
              key={l}
              onClick={() => setLang(l)}
              style={{
                width: 36, height: '100%', border: 'none', cursor: 'pointer',
                fontFamily: '"IBM Plex Mono", monospace', fontSize: 9, fontWeight: 700,
                letterSpacing: '0.12em', textTransform: 'uppercase',
                background: lang === l ? '#B8975A' : 'transparent',
                color: lang === l ? '#000' : '#3d3a30',
                borderLeft: l === 'en' ? '1px solid rgba(184,151,90,0.12)' : 'none',
                transition: 'all 0.15s',
              }}
            >
              {l.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Icons */}
        {[
          { icon: 'tune',                    hasAlert: false },
          { icon: 'notifications',           hasAlert: true  },
          { icon: 'account_balance_wallet',  hasAlert: false },
        ].map(({ icon, hasAlert }) => (
          <button
            key={icon}
            style={{
              width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'none', border: 'none', borderLeft: '1px solid rgba(184,151,90,0.12)',
              cursor: 'pointer', position: 'relative', transition: 'background 0.15s',
            }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(184,151,90,0.08)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 17, color: '#3d3a30' }}>{icon}</span>
            {hasAlert && (
              <span style={{
                position: 'absolute', top: 10, right: 10,
                width: 5, height: 5, background: '#B8975A', borderRadius: '50%',
                border: '1px solid #0c0e1a',
              }} />
            )}
          </button>
        ))}

        {/* Avatar */}
        <div style={{ width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center', borderLeft: '1px solid rgba(184,151,90,0.12)', cursor: 'pointer' }}>
          <div style={{ width: 28, height: 28, border: '1px solid rgba(184,151,90,0.3)', background: '#111425', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: '#3d3a30' }}>person</span>
          </div>
        </div>
      </div>
    </header>
  )
}

/* ── Animated routes ─────────────────────────────────────────────────── */
function AnimatedRoutes() {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.22, ease: 'easeInOut' }}
        className="h-full"
      >
        <Routes location={location}>
          <Route path="/"         element={<HomePage />} />
          <Route path="/search"   element={<SearchPage />} />
          <Route path="/agents"   element={<AgentsPage />} />
          <Route path="/alerts"   element={<AlertsPage />} />
          <Route path="/auctions" element={<AuctionsPage />} />
          <Route path="/catalog"  element={<CatalogPage />} />
          <Route path="/encyclopedia/:reference" element={<EncyclopediaDetailPage />} />
          <Route path="/verify"   element={<VerificationPage />} />
          <Route path="/opt-out"  element={<OptOutPage />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  )
}

/* ── App ─────────────────────────────────────────────────────────────── */
export default function App() {
  const { unlocked, unlock } = useSplashGate()

  if (!unlocked) return <SplashGate onUnlock={unlock} />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', background: '#07080f' }}>
      <Ticker />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
          <TopBar />
          <main style={{ flex: 1, overflowY: 'auto' }}>
            <AnimatedRoutes />
          </main>
          <footer
            style={{
              height: 22,
              background: '#060810',
              borderTop: '1px solid rgba(184,151,90,0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0 20px',
              fontFamily: '"IBM Plex Mono", monospace',
              fontSize: 8,
              color: '#3d3a30',
              letterSpacing: '0.08em',
            }}
          >
            <span>WATCHSCANNER.IT © 2026</span>
            <span>CHRONO24 · EBAY · INSTAGRAM · AUCTION HOUSES</span>
          </footer>
        </div>
      </div>
    </div>
  )
}
