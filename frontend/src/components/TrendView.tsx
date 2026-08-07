import { useMemo, useState } from 'react'
import TrendBadge from './TrendBadge'
import TrendChart from './TrendChart'
import { findVerdict, statusFor } from '../lib/trends'
import type { TrendScope, TrendVerdict, TrendsTimeseriesFile } from '../types'

const SCOPE_LABEL: Record<TrendScope, string> = {
  google_play: 'Google Play (9-year baseline)',
  app_store: 'App Store (~9-month history)',
  combined_overlap: 'Combined (Nov 2025 onward only)',
}

function VerdictRow({
  v,
  active,
  onClick,
}: {
  v: TrendVerdict
  active: boolean
  onClick: () => void
}) {
  const sign = (v.pp_delta ?? 0) >= 0 ? '+' : ''
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-2.5 text-left border-l-2 ${
        active ? 'border-stone-800 bg-stone-50' : 'border-transparent hover:bg-stone-50'
      }`}
    >
      <span className="flex-1 text-sm font-medium text-stone-800">
        {v.category_name}
        {v.watch_category && (
          <span className="ml-2 rounded-full bg-amber-100 text-amber-800 text-[10px] font-medium px-1.5 py-0.5 align-middle">
            watch
          </span>
        )}
      </span>
      <span className="text-xs text-stone-400">{v.level}</span>
      <span
        className={`text-sm tabular-nums font-medium ${
          v.flagged_spike ? 'text-rust-600' : v.flagged_decline ? 'text-sage-600' : ''
        }`}
      >
        {sign}
        {v.pp_delta?.toFixed(1)}pp
      </span>
      <span className="w-24 text-right text-xs tabular-nums text-stone-400">
        {v.baseline_rate_pct?.toFixed(1)}% → {v.recent_rate_pct?.toFixed(1)}%
      </span>
    </button>
  )
}

export default function TrendView({
  verdicts,
  timeseries,
  focusedCategory,
  onFocusCategory,
  onSelectCategory,
}: {
  verdicts: TrendVerdict[]
  timeseries: TrendsTimeseriesFile
  focusedCategory: string | null
  onFocusCategory: (categoryId: string) => void
  onSelectCategory: (categoryId: string) => void
}) {
  const [scope, setScope] = useState<TrendScope>('google_play')

  const scoped = useMemo(() => verdicts.filter((v) => v.scope === scope), [verdicts, scope])
  const rising = useMemo(
    () => scoped.filter((v) => v.flagged_spike).sort((a, b) => (b.pp_delta ?? 0) - (a.pp_delta ?? 0)),
    [scoped],
  )
  const falling = useMemo(
    () => scoped.filter((v) => v.flagged_decline).sort((a, b) => (a.pp_delta ?? 0) - (b.pp_delta ?? 0)),
    [scoped],
  )

  const activeCategory = focusedCategory ?? rising[0]?.category_id ?? falling[0]?.category_id ?? null
  const activeVerdict = activeCategory ? findVerdict(verdicts, scope, activeCategory) : undefined
  const activeStatus = statusFor(activeVerdict)
  const chartData = activeCategory ? timeseries[scope]?.[activeCategory] ?? [] : []

  return (
    <div className="rounded-2xl border border-stone-200 bg-white">
      <div className="flex items-center justify-between border-b border-stone-100 px-6 py-3.5">
        <h3 className="font-serif text-base font-medium text-stone-900">Trend view</h3>
        <select
          value={scope}
          onChange={(e) => setScope(e.target.value as TrendScope)}
          className="rounded border border-stone-200 bg-white px-2 py-1 text-sm text-stone-700"
        >
          {(Object.keys(SCOPE_LABEL) as TrendScope[]).map((s) => (
            <option key={s} value={s}>
              {SCOPE_LABEL[s]}
            </option>
          ))}
        </select>
      </div>

      {scope === 'combined_overlap' && (
        <p className="px-6 pt-3 text-xs text-stone-500">
          Combined data only covers Nov 2025 onward — the window where both sources actually
          have coverage. Never mixed with Google Play's longer standalone history.
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-0 md:divide-x divide-stone-100">
        <div>
          <p className="px-4 pt-3 pb-1 text-xs font-medium uppercase tracking-wide text-rust-600">
            Rising ({rising.length})
          </p>
          {rising.length === 0 && (
            <p className="px-4 pb-3 text-sm text-stone-400">Nothing flagged this scope.</p>
          )}
          {rising.map((v) => (
            <VerdictRow
              key={`${v.scope}-${v.category_id}`}
              v={v}
              active={v.category_id === activeCategory}
              onClick={() => onFocusCategory(v.category_id)}
            />
          ))}
        </div>
        <div>
          <p className="px-4 pt-3 pb-1 text-xs font-medium uppercase tracking-wide text-sage-600">
            Falling ({falling.length})
          </p>
          {falling.length === 0 && (
            <p className="px-4 pb-3 text-sm text-stone-400">Nothing flagged this scope.</p>
          )}
          {falling.map((v) => (
            <VerdictRow
              key={`${v.scope}-${v.category_id}`}
              v={v}
              active={v.category_id === activeCategory}
              onClick={() => onFocusCategory(v.category_id)}
            />
          ))}
        </div>
      </div>

      {activeCategory && (
        <div className="border-t border-stone-100 p-6">
          <div className="mb-3 flex items-center gap-3">
            <p className="text-sm text-stone-500 flex-1">
              Monthly rate —{' '}
              <span className="font-medium text-stone-800">
                {activeVerdict?.category_name ?? activeCategory}
              </span>
            </p>
            <TrendBadge status={activeStatus} />
            <button
              onClick={() => onSelectCategory(activeCategory)}
              className="rounded-full border border-stone-200 px-2.5 py-1 text-xs font-medium text-stone-600 hover:border-stone-400 hover:text-stone-900"
            >
              Browse reviews →
            </button>
          </div>
          {activeStatus === 'stable' && (
            <p className="mb-3 text-xs text-stone-500">
              Not flagged as rising or falling this period — shown because it was selected from
              the breakdown, not because it moved. Large, steady categories matter too.
            </p>
          )}
          <TrendChart data={chartData} status={activeStatus} />
        </div>
      )}
    </div>
  )
}
