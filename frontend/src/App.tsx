import { useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import WatchBackground from './components/WatchBackground'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import AgentsPage from './pages/AgentsPage'
import AlertsPage from './pages/AlertsPage'
import AuctionsPage from './pages/AuctionsPage'
import CatalogPage from './pages/CatalogPage'
import EncyclopediaDetailPage from './pages/EncyclopediaDetailPage'
import VerificationPage from './pages/VerificationPage'
import { useLang } from './lib/lang'

function TopBar() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const { t, lang, setLang } = useLang()

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && query.trim()) {
      navigate(`/search?ref=${encodeURIComponent(query.trim())}`)
      setQuery('')
    }
  }

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between px-8 h-16 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800">
      {/* Left: search + top nav */}
      <div className="flex items-center gap-8">
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-zinc-500 text-sm leading-none">
            search
          </span>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleSearch}
            placeholder={t.searchPlaceholder}
            className="bg-zinc-900 border border-zinc-800 text-xs py-2 pl-10 pr-4 w-64 focus:outline-none focus:border-yellow-400 transition-colors rounded text-zinc-300 placeholder-zinc-600"
          />
        </div>
      </div>

      {/* Right: lang toggle + icons + avatar */}
      <div className="flex items-center gap-5">
        {/* Language selector */}
        <div className="flex items-center bg-zinc-900 border border-zinc-800 rounded overflow-hidden">
          <button
            onClick={() => setLang('it')}
            className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest transition-colors ${
              lang === 'it' ? 'bg-yellow-400 text-zinc-950' : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            IT
          </button>
          <button
            onClick={() => setLang('en')}
            className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest transition-colors ${
              lang === 'en' ? 'bg-yellow-400 text-zinc-950' : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            EN
          </button>
        </div>

        <div className="flex items-center gap-4 text-zinc-400">
          <button className="hover:text-yellow-400 transition-colors">
            <span className="material-symbols-outlined">tune</span>
          </button>
          <button className="hover:text-yellow-400 transition-colors">
            <span className="material-symbols-outlined">account_balance_wallet</span>
          </button>
          <button className="hover:text-yellow-400 transition-colors relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-yellow-400 rounded-full" />
          </button>
        </div>
        <div className="h-8 w-8 rounded-full border border-yellow-400/30 bg-zinc-800 flex items-center justify-center">
          <span className="material-symbols-outlined text-zinc-400 text-sm">person</span>
        </div>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950">
      <WatchBackground />
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto fade-in">
          <Routes>
            <Route path="/"        element={<HomePage />} />
            <Route path="/search"  element={<SearchPage />} />
            <Route path="/agents"  element={<AgentsPage />} />
            <Route path="/alerts"  element={<AlertsPage />} />
            <Route path="/auctions" element={<AuctionsPage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/encyclopedia/:reference" element={<EncyclopediaDetailPage />} />
            <Route path="/verify" element={<VerificationPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
