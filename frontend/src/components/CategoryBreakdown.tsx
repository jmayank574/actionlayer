import { useState } from 'react'
import TrendBadge from './TrendBadge'
import { findVerdict, statusFor } from '../lib/trends'
import type { ParentSnapshot, TrendVerdict } from '../types'

function WatchBadge() {
  return (
    <span className="rounded-full bg-amber-100 text-amber-800 text-[11px] font-medium px-2 py-0.5">
      watch
    </span>
  )
}

function Bar({ pct, tone }: { pct: number | null; tone: 'parent' | 'sub' }) {
  const width = pct == null ? 0 : Math.min(100, (pct / 25) * 100) // 25% ~= full bar, headroom for outliers
  return (
    <div className={`h-1.5 w-full rounded-full ${tone === 'parent' ? 'bg-stone-200' : 'bg-stone-100'}`}>
      <div
        className={`h-1.5 rounded-full ${tone === 'parent' ? 'bg-stone-700' : 'bg-stone-400'}`}
        style={{ width: `${width}%` }}
      />
    </div>
  )
}

function ViewReviewsButton({ onClick, count }: { onClick: () => void; count: number }) {
  return (
    <button
      onClick={onClick}
      className="shrink-0 rounded-full border border-stone-200 bg-white px-2.5 py-1 text-[11px] font-medium text-stone-600 hover:border-stone-400 hover:text-stone-900 transition-colors"
    >
      {count.toLocaleString()} reviews →
    </button>
  )
}

export default function CategoryBreakdown({
  parents,
  otherUngrouped,
  totalReviews,
  verdicts,
  onSelectCategory,
  onFocusTrend,
}: {
  parents: ParentSnapshot[]
  otherUngrouped: { count: number; rate_pct: number | null }
  totalReviews: number
  verdicts: TrendVerdict[]
  onSelectCategory: (categoryId: string) => void
  onFocusTrend: (categoryId: string) => void
}) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const sorted = [...parents].sort((a, b) => (b.rate_pct ?? 0) - (a.rate_pct ?? 0))

  function toggle(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <div className="rounded-2xl border border-stone-200 bg-white overflow-hidden">
      <div className="border-b border-stone-100 bg-stone-50/70 px-6 py-3 text-sm text-stone-500">
        {totalReviews.toLocaleString()} reviews tagged · {otherUngrouped.count.toLocaleString()}{' '}
        ({otherUngrouped.rate_pct?.toFixed(1)}%) Other/Ungrouped
      </div>
      <ul className="divide-y divide-stone-100">
        {sorted.map((p) => {
          const verdict = findVerdict(verdicts, 'google_play', p.id)
          const status = statusFor(verdict)
          return (
            <li key={p.id}>
              <div className="flex items-center gap-3 px-6 py-4">
                <button
                  onClick={() => toggle(p.id)}
                  className="w-4 text-stone-400 hover:text-stone-700"
                  aria-label="expand"
                >
                  {expanded.has(p.id) ? '▾' : '▸'}
                </button>
                <button
                  onClick={() => onFocusTrend(p.id)}
                  className="flex-1 text-left font-serif text-[17px] font-medium text-stone-900 hover:text-stone-600"
                >
                  {p.name}
                </button>
                {p.watch_category && <WatchBadge />}
                <TrendBadge
                  status={status}
                  title={
                    verdict?.baseline_rate_pct != null && verdict?.recent_rate_pct != null
                      ? `${verdict.baseline_rate_pct.toFixed(1)}% baseline → ${verdict.recent_rate_pct.toFixed(1)}% recent`
                      : 'Not enough recent/baseline volume to judge'
                  }
                />
                <span className="hidden sm:block w-24">
                  <Bar pct={p.rate_pct} tone="parent" />
                </span>
                <span className="w-16 text-right text-sm tabular-nums font-medium text-stone-700">
                  {p.rate_pct?.toFixed(1)}%
                </span>
                <ViewReviewsButton onClick={() => onSelectCategory(p.id)} count={p.count} />
              </div>
              {expanded.has(p.id) && (
                <ul className="ml-10 mr-6 mb-4 border-l-2 border-stone-100 pl-4">
                  {[...p.subcategories]
                    .sort((a, b) => (b.rate_pct ?? 0) - (a.rate_pct ?? 0))
                    .map((s) => {
                      const subVerdict = findVerdict(verdicts, 'google_play', s.id)
                      const subStatus = statusFor(subVerdict)
                      return (
                        <li key={s.id} className="flex items-center gap-3 py-2">
                          <button
                            onClick={() => onFocusTrend(s.id)}
                            className="flex-1 text-left text-sm text-stone-600 hover:text-stone-900"
                          >
                            {s.name}
                          </button>
                          {s.watch_category && <WatchBadge />}
                          <TrendBadge status={subStatus} />
                          <span className="hidden sm:block w-20">
                            <Bar pct={s.rate_pct} tone="sub" />
                          </span>
                          <span className="w-14 text-right text-xs tabular-nums text-stone-500">
                            {s.rate_pct?.toFixed(1)}%
                          </span>
                          <ViewReviewsButton onClick={() => onSelectCategory(s.id)} count={s.count} />
                        </li>
                      )
                    })}
                </ul>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
