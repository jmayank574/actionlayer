import type { ParentSnapshot, TrendVerdict } from '../types'

const VERDICT_LABEL: Record<string, string> = {
  spike: 'Spiking',
  decline: 'Declining',
  stable: 'Stable',
  emerging_new_category: 'Emerging',
  insufficient_recent_occurrences: 'Too few recent mentions to judge',
  insufficient_baseline_volume: 'Baseline too thin to judge',
}

function verdictTone(v: string, flaggedSpike: boolean, flaggedDecline: boolean) {
  if (flaggedSpike) return 'text-rust-700 bg-rust-50'
  if (flaggedDecline) return 'text-sage-700 bg-sage-50'
  if (v.startsWith('insufficient')) return 'text-stone-400 bg-stone-50'
  return 'text-stone-600 bg-stone-50'
}

export default function WatchCategoryPanel({
  watchParents,
  verdicts,
  onSelectCategory,
}: {
  watchParents: ParentSnapshot[]
  verdicts: TrendVerdict[]
  onSelectCategory: (categoryId: string) => void
}) {
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50/40">
      <div className="border-b border-amber-200/70 px-6 py-3.5">
        <h3 className="font-serif text-base font-medium text-stone-900">Watch categories</h3>
        <p className="text-xs text-stone-500 mt-0.5">
          Called out on every view regardless of volume rank — low frequency here doesn't mean
          low stakes (see taxonomy.yaml watch_reason).
        </p>
      </div>
      <div className="divide-y divide-amber-200/50">
        {watchParents.map((p) => {
          const gp = verdicts.find((v) => v.scope === 'google_play' && v.category_id === p.id)
          const as = verdicts.find((v) => v.scope === 'app_store' && v.category_id === p.id)
          return (
            <div key={p.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => onSelectCategory(p.id)}
                  className="font-medium text-stone-900 hover:underline"
                >
                  {p.name}
                </button>
                <span className="text-sm tabular-nums text-stone-500">
                  {p.rate_pct?.toFixed(1)}% overall ({p.count} reviews)
                </span>
              </div>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                {(
                  [
                    ['google_play', gp],
                    ['app_store', as],
                  ] as const
                ).map(([label, v]) =>
                  v ? (
                    <span
                      key={label as string}
                      className={`rounded-full px-2 py-1 ${verdictTone(v.verdict, v.flagged_spike, v.flagged_decline)}`}
                    >
                      {label}: {VERDICT_LABEL[v.verdict] ?? v.verdict}
                      {v.recent_rate_pct != null && v.baseline_rate_pct != null && (
                        <> ({v.baseline_rate_pct.toFixed(1)}% → {v.recent_rate_pct.toFixed(1)}%)</>
                      )}
                    </span>
                  ) : null,
                )}
              </div>
              {p.watch_reason && (
                <p className="mt-2 text-xs text-stone-500 leading-relaxed">{p.watch_reason}</p>
              )}
            </div>
          )
        })}
        {watchParents.length === 0 && (
          <p className="px-6 py-4 text-sm text-stone-400">
            No categories are flagged as watch categories in taxonomy.yaml.
          </p>
        )}
      </div>
    </div>
  )
}
