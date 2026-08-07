import { BROKEN_BASICS_IDS, FEATURE_REQUEST_ID } from '../lib/trends'
import type { ParentSnapshot } from '../types'

export default function BrokenBasicsCallout({
  parents,
  onSelectCategory,
}: {
  parents: ParentSnapshot[]
  onSelectCategory: (categoryId: string) => void
}) {
  const byId = new Map(parents.map((p) => [p.id, p]))
  const brokenBasics = BROKEN_BASICS_IDS.map((id) => byId.get(id)).filter(
    (p): p is ParentSnapshot => !!p,
  )
  const featureRequests = byId.get(FEATURE_REQUEST_ID)

  if (brokenBasics.length === 0 || !featureRequests) return null

  const brokenPct = brokenBasics.reduce((sum, p) => sum + (p.rate_pct ?? 0), 0)
  const featurePct = featureRequests.rate_pct ?? 0
  const ratio = featurePct > 0 ? brokenPct / featurePct : null
  const maxPct = Math.max(brokenPct, featurePct, 1)

  return (
    <div className="rounded-2xl border border-stone-200 border-l-4 border-l-rust-500 bg-white p-6">
      <p className="text-xs font-semibold uppercase tracking-wide text-stone-400 mb-2">
        Structural read on this dataset
      </p>
      <p className="font-serif text-xl leading-snug text-stone-900">
        <span className="font-semibold text-rust-600">{brokenPct.toFixed(1)}%</span> of tagged
        feedback is about things not working
        {ratio && (
          <>
            {' '}
            — <span className="font-semibold">{ratio.toFixed(1)}×</span> more often than
          </>
        )}{' '}
        <span className="font-semibold text-stone-900">{featurePct.toFixed(1)}%</span> requesting
        new features.
      </p>

      <div className="mt-5 space-y-3">
        <div>
          <div className="mb-1 flex items-center justify-between text-xs text-stone-500">
            <span>Not working ({brokenBasics.map((p) => p.name).join(' + ')})</span>
            <span className="tabular-nums">{brokenPct.toFixed(1)}%</span>
          </div>
          <div className="h-2 rounded-full bg-stone-100">
            <div
              className="h-2 rounded-full bg-rust-500"
              style={{ width: `${(brokenPct / maxPct) * 100}%` }}
            />
          </div>
        </div>
        <div>
          <div className="mb-1 flex items-center justify-between text-xs text-stone-500">
            <span>{featureRequests.name}</span>
            <span className="tabular-nums">{featurePct.toFixed(1)}%</span>
          </div>
          <div className="h-2 rounded-full bg-stone-100">
            <div
              className="h-2 rounded-full bg-stone-400"
              style={{ width: `${(featurePct / maxPct) * 100}%` }}
            />
          </div>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {[...brokenBasics, featureRequests].map((p) => (
          <button
            key={p.id}
            onClick={() => onSelectCategory(p.id)}
            className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs text-stone-600 hover:border-stone-400 hover:text-stone-900 transition-colors"
          >
            {p.name} · {p.rate_pct?.toFixed(1)}%
          </button>
        ))}
      </div>
    </div>
  )
}
