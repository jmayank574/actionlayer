import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Sparkles, Compass, ChevronsLeft, ChevronsRight, ChevronDown, LogOut } from 'lucide-react'

interface NavItem {
  label: string
  icon: React.ComponentType<{ size?: number; strokeWidth?: number }>
  to?: string
}

// Only Home, Assistant, Explore for now -- the rest of the shell (Feedback,
// Boards, Alerts, Integrations, Organizations, Digests, Support) is deferred
// until there's something real behind them.
const NAV_ITEMS: NavItem[] = [
  { label: 'Home', icon: Home, to: '/' },
  { label: 'Assistant', icon: Sparkles },
  { label: 'Explore', icon: Compass },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const isHome = location.pathname === '/' || location.pathname.startsWith('/category')

  return (
    <aside
      className={`shrink-0 bg-sidebar text-stone-600 flex flex-col border-r border-stone-200 transition-[width] duration-200 ${
        collapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      <div className="flex items-center justify-between px-4 pt-5 pb-6">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-rust-500 text-white">
              <Sparkles size={14} strokeWidth={2} />
            </div>
            <span className="font-serif text-[15px] font-medium text-stone-900">ActionLayer</span>
          </div>
        )}
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="rounded-md p-1.5 text-stone-400 hover:bg-sidebar-raised hover:text-stone-700"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
        </button>
      </div>

      <nav className="flex-1 px-3 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const active = item.to !== undefined && isHome
          const Icon = item.icon
          const content = (
            <>
              <Icon size={17} strokeWidth={1.9} />
              {!collapsed && <span className="text-[13.5px]">{item.label}</span>}
            </>
          )
          const className = `flex items-center gap-3 rounded-full px-3 py-2 transition-colors ${
            active
              ? 'bg-rust-500 text-white font-medium'
              : item.to
                ? 'text-stone-600 hover:bg-sidebar-raised hover:text-stone-900'
                : 'text-stone-400 hover:bg-sidebar-raised hover:text-stone-600'
          }`

          if (item.to) {
            return (
              <Link key={item.label} to={item.to} className={className} title={collapsed ? item.label : undefined}>
                {content}
              </Link>
            )
          }
          return (
            <div key={item.label} className={className} title={collapsed ? `${item.label} — coming soon` : `${item.label} — coming soon`}>
              {content}
            </div>
          )
        })}
      </nav>

      <div className="border-t border-stone-200 px-3 py-4">
        <button className="flex w-full items-center gap-2.5 rounded-xl px-2 py-1.5 hover:bg-sidebar-raised transition-colors">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-stone-700 font-serif text-xs font-medium text-cream">
            MJ
          </div>
          {!collapsed && (
            <>
              <div className="min-w-0 flex-1 text-left">
                <p className="truncate text-[13px] font-medium text-stone-800">Mayank Joshi</p>
                <p className="truncate text-[11px] text-stone-500">ActionLayer</p>
              </div>
              <ChevronDown size={14} className="text-stone-400" />
            </>
          )}
        </button>
        {!collapsed && (
          <button className="mt-1 flex items-center gap-2.5 rounded-xl px-2 py-1.5 text-stone-400 hover:bg-sidebar-raised hover:text-stone-700 transition-colors">
            <LogOut size={15} strokeWidth={1.9} />
            <span className="text-[12px]">Sign out</span>
          </button>
        )}
      </div>
    </aside>
  )
}
