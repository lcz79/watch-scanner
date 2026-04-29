import { NavLink } from 'react-router-dom'
import { Search, Home, Bot, Bell, LayoutGrid } from 'lucide-react'
import { clsx } from 'clsx'

const nav = [
  { to: '/', icon: Home, label: 'Dashboard', sub: 'Home' },
  { to: '/catalog', icon: LayoutGrid, label: 'Catalogo', sub: 'Orologi disponibili' },
  { to: '/search', icon: Search, label: 'Cerca', sub: 'Ricerca prezzi' },
  { to: '/agents', icon: Bot, label: 'Agenti', sub: 'Gestione bot' },
  { to: '/alerts', icon: Bell, label: 'Alert', sub: 'Notifiche' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 flex flex-col bg-zinc-900 shadow-[1px_0_0_0_theme(colors.zinc.800)]">
      {/* Logo */}
      <div className="py-8 px-5 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gold-400 flex items-center justify-center shrink-0">
            <svg viewBox="0 0 32 32" className="w-6 h-6">
              <circle cx="16" cy="16" r="10" fill="none" stroke="#111" strokeWidth="2.5" />
              <circle cx="16" cy="16" r="1.5" fill="#111" />
              <line x1="16" y1="8" x2="16" y2="16" stroke="#111" strokeWidth="2" strokeLinecap="round" />
              <line x1="16" y1="16" x2="21" y2="16" stroke="#111" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <div className="min-w-0">
            <p className="font-display font-bold text-lg text-zinc-100 leading-tight truncate">
              WatchScanner
            </p>
            <p className="text-xs text-zinc-500 leading-tight">Trova il prezzo migliore</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {nav.map(({ to, icon: Icon, label, sub }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-gold-400/10 text-gold-400 border-l-2 border-gold-400'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 border-l-2 border-transparent'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={18} className="shrink-0" />
                <div className="min-w-0">
                  <p className="leading-tight">{label}</p>
                  <p
                    className={clsx(
                      'text-[10px] leading-tight font-normal transition-colors duration-150',
                      isActive ? 'text-gold-400/60' : 'text-zinc-600 group-hover:text-zinc-500'
                    )}
                  >
                    {sub}
                  </p>
                </div>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Status */}
      <div className="border-t border-zinc-800 px-5 py-4 space-y-1">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-emerald-400 rounded-full pulse-dot shrink-0" />
          <span className="text-xs text-emerald-400 font-medium">Sistema attivo</span>
        </div>
        <p className="text-xs text-zinc-600 pl-4">v1.0</p>
      </div>
    </aside>
  )
}
