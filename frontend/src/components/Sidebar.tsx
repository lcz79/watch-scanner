import { NavLink } from 'react-router-dom'
import { useLang } from '../lib/lang'

export default function Sidebar() {
  const { t } = useLang()

  const nav = [
    { to: '/',        icon: 'dashboard',           label: t.dashboard },
    { to: '/search',  icon: 'query_stats',          label: t.marketFeed },
    { to: '/catalog', icon: 'menu_book',             label: t.portfolio },
    { to: '/alerts',  icon: 'notifications_active', label: t.priceAlerts },
    { to: '/auctions', icon: 'gavel',               label: t.auctionsNav },
    { to: '/agents',  icon: 'monitoring',           label: t.analytics },
  ]

  return (
    <aside className="w-[224px] shrink-0 flex flex-col bg-zinc-900 border-r border-zinc-800 relative z-10 h-screen">

      {/* Branding */}
      <div className="mb-10 px-5 pt-6">
        <h1 className="text-yellow-400 font-bold tracking-widest uppercase font-display-price text-lg leading-none">
          WatchScanner
        </h1>
        <p className="text-[10px] text-zinc-500 font-mono tracking-widest uppercase mt-1">
          Terminal v1.0
        </p>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-1 overflow-y-auto">
        {nav.map(({ to, icon, label }) => (
          <NavLink
            key={to + label}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              isActive
                ? 'flex items-center gap-3 px-3 py-2.5 text-yellow-400 font-bold border-r-2 border-yellow-400 bg-zinc-800/50 transition-all duration-200'
                : 'flex items-center gap-3 px-3 py-2.5 text-zinc-400 hover:text-yellow-400 hover:bg-zinc-800 transition-all duration-200'
            }
          >
            <span className="material-symbols-outlined text-xl leading-none">{icon}</span>
            <span className="font-['Space_Grotesk'] text-sm tracking-tight">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="mt-auto space-y-1 pt-6 border-t border-zinc-800 px-3 pb-4">
        <button className="w-full mb-4 py-3 bg-primary text-on-primary font-bold rounded text-xs uppercase tracking-widest transition-opacity hover:opacity-90">
          {t.upgradePro}
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-2.5 text-zinc-400 hover:text-zinc-100 transition-all duration-200">
          <span className="material-symbols-outlined text-xl leading-none">help</span>
          <span className="font-['Space_Grotesk'] text-sm tracking-tight">{t.support}</span>
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-2.5 text-zinc-400 hover:text-zinc-100 transition-all duration-200">
          <span className="material-symbols-outlined text-xl leading-none">settings</span>
          <span className="font-['Space_Grotesk'] text-sm tracking-tight">{t.settings}</span>
        </button>
      </div>
    </aside>
  )
}
