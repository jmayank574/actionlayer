import { useMemo } from 'react'
import TrendBadge from './TrendBadge'
import TrendChart from './TrendChart'
import { findVerdict, statusFor } from '../lib/trends'
import type { TrendScope, TrendVerdict, TrendsTimeseriesFile } from '../types'

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
        {v.recent_pct_positive != null && (
          <span className="block text-[11px] font-normal text-stone-400 mt-0.5">
            {v.recent_pct_positive}% positive
            {v.sentiment_delta != null && (
              <span className={v.sentiment_delta >= 0 ? 'text-sage-600' : 'text-rust-600'}>
                {' '}({v.sentiment_delta >= 0 ? '+' : ''}
                {v.sentiment_delta}pp)
              </span>
            )}
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
  scope,
  focusedCategory,
  onFocusCategory,
  onSelectCategory,
}: {
  verdicts: TrendVerdict[]
  timeseries: TrendsTimeseriesFile
  scope: TrendScope
  focusedCategory: string | null
  onFocusCategory: (categoryId: string) => void
  onSelectCategory: (categoryId: string) => void
}) {
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
      <div className="border-b border-stone-100 px-6 py-3.5">
        <h3 className="font-serif text-base font-medium text-stone-900">Trend view</h3>
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
          {activeVerdict?.recent_pct_positive != null && (
            <p className="mb-3 text-xs text-stone-500">
              <span className="font-medium text-sage-600">{activeVerdict.recent_pct_positive}% positive</span>
              {' · '}
              <span className="font-medium text-rust-600">{activeVerdict.recent_pct_negative}% negative</span>
              {' — 4-5★ vs. 1-2★ of reviews mentioning this, recent window'}
              {activeVerdict.sentiment_delta != null && (
                <>
                  {', '}
                  {activeVerdict.sentiment_delta >= 0 ? 'up' : 'down'} {Math.abs(activeVerdict.sentiment_delta)}pp
                  positive vs. baseline
                </>
              )}
              {'. Whole-review rating, not specific to this one topic.'}
            </p>
          )}
          <TrendChart data={chartData} status={activeStatus} />
        </div>
      )}
    </div>
  )
}
