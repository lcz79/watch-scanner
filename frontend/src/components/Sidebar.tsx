import { NavLink } from 'react-router-dom'
import { useLang } from '../lib/lang'

export default function Sidebar() {
  const { t } = useLang()

  const nav = [
    { to: '/',         icon: 'grid_view',             label: 'Home' },
    { to: '/search',   icon: 'search',                label: t.marketFeed },
    { to: '/auctions', icon: 'gavel',                 label: t.auctionsNav },
    { to: '/alerts',   icon: 'notifications',         label: t.priceAlerts },
    { to: '/agents',   icon: 'auto_graph',            label: t.analytics },
    { to: '/catalog',  icon: 'menu_book',             label: t.portfolio },
  ]

  return (
    <aside
      style={{ background: '#0c0e1a', borderRight: '1px solid rgba(184,151,90,0.12)' }}
      className="w-16 shrink-0 flex flex-col items-center pt-3 gap-0.5 h-screen relative z-10"
    >
      {/* Logo */}
      <div
        style={{ borderBottom: '1px solid rgba(184,151,90,0.12)' }}
        className="w-full flex flex-col items-center justify-center py-3 mb-2"
      >
        <span
          style={{ fontFamily: '"Playfair Display", serif', color: '#B8975A', fontSize: 15 }}
          className="font-black leading-none"
        >
          WS
        </span>
        <span
          style={{ fontFamily: '"IBM Plex Mono", monospace', color: '#3d3a30', fontSize: 7, letterSpacing: '0.18em' }}
          className="uppercase mt-0.5"
        >
          v2
        </span>
      </div>

      {/* Nav items */}
      {nav.map(({ to, icon, label }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={() => ''}
          style={({ isActive }) => ({
            width: 48,
            height: 44,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
            cursor: 'pointer',
            textDecoration: 'none',
            borderLeft: isActive ? '2px solid #B8975A' : '2px solid transparent',
            background: isActive ? 'rgba(184,151,90,0.08)' : 'transparent',
            transition: 'all 0.15s',
          })}
        >
          {({ isActive }) => (
            <>
              <span
                className="material-symbols-outlined leading-none"
                style={{ fontSize: 17, color: isActive ? '#B8975A' : '#3d3a30' }}
              >
                {icon}
              </span>
              <span
                style={{
                  fontFamily: '"IBM Plex Mono", monospace',
                  fontSize: 6,
                  letterSpacing: '0.1em',
                  color: isActive ? '#B8975A' : '#3d3a30',
                  textTransform: 'uppercase',
                }}
              >
                {label.slice(0, 6)}
              </span>
            </>
          )}
        </NavLink>
      ))}

      <div className="flex-1" />

      {/* Bottom items */}
      <div
        style={{ borderTop: '1px solid rgba(184,151,90,0.08)' }}
        className="w-full flex flex-col items-center py-2 gap-0.5"
      >
        <a
          href="https://uptimerobot.com"
          target="_blank"
          rel="noopener noreferrer"
          style={{ width: 48, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', textDecoration: 'none' }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#3d3a30' }}>monitor_heart</span>
        </a>
        <button style={{ width: 48, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'none', border: 'none', cursor: 'pointer' }}>
          <span className="material-symbols-outlined" style={{ fontSize: 16, color: '#3d3a30' }}>settings</span>
        </button>
      </div>
    </aside>
  )
}
