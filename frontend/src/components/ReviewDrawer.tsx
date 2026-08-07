import { useState } from 'react'
import type { CategoryMetaFile, InsightCard, ReviewSamplesFile } from '../types'

// Context relocated off the primary insight card (per the card-simplification
// pass) lives here instead, collapsed by default -- reachable, not deleted.
function InsightContext({ card }: { card: InsightCard }) {
  const [open, setOpen] = useState(false)
  const hasExtra = !!card.multi_label_note || !!card.watch_reason || card.top_drivers.length > 0
  if (!hasExtra) return null

  return (
    <div className="border-b border-stone-100 px-6 py-3">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between text-left text-xs font-medium text-stone-500 hover:text-stone-800"
      >
        <span>Why this is here</span>
        <span>{open ? '▾' : '▸'}</span>
      </button>
      {open && (
        <div className="mt-3 space-y-3 text-xs leading-relaxed text-stone-500">
          {card.watch_reason && <p>{card.watch_reason}</p>}
          {card.multi_label_note && <p>{card.multi_label_note}</p>}
          {card.top_drivers.length > 0 && (
            <div>
              <p className="mb-1.5 font-medium text-stone-600">Driven by:</p>
              <ul className="space-y-1">
                {card.top_drivers.map((d) => {
                  const sign = (d.pp_delta ?? 0) >= 0 ? '+' : ''
                  return (
                    <li key={d.category_id} className="flex justify-between gap-2">
                      <span>{d.name}</span>
                      <span className="tabular-nums">
                        {sign}
                        {d.pp_delta?.toFixed(1) ?? '–'}pp
                      </span>
                    </li>
                  )
                })}
              </ul>
            </div>
          )}
          <p className="text-stone-400">
            Based on {card.recent_count} of {card.recent_total} reviews this window, vs.{' '}
            {card.baseline_count} of {card.baseline_total} in the trailing baseline.
          </p>
        </div>
      )}
    </div>
  )
}

export default function ReviewDrawer({
  categoryId,
  meta,
  samples,
  insightCard,
  onClose,
}: {
  categoryId: string | null
  meta: CategoryMetaFile
  samples: ReviewSamplesFile
  insightCard?: InsightCard
  onClose: () => void
}) {
  if (!categoryId) return null
  const info = meta[categoryId]
  const reviews = samples[categoryId] ?? []

  return (
    <>
      <div className="fixed inset-0 bg-stone-900/30 z-40" onClick={onClose} />
      <aside className="fixed right-0 top-0 z-50 h-full w-full max-w-lg overflow-y-auto border-l border-stone-200 bg-cream-raised shadow-xl">
        <div className="sticky top-0 flex items-center justify-between border-b border-stone-100 bg-cream-raised px-6 py-4">
          <div>
            <h3 className="font-serif text-lg font-medium text-stone-900">{info?.name ?? categoryId}</h3>
            <p className="text-xs text-stone-500">
              {reviews.length} most-recent review{reviews.length === 1 ? '' : 's'} of up to 30
              sampled
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-1.5 text-stone-400 hover:bg-stone-100 hover:text-stone-700"
            aria-label="close"
          >
            ✕
          </button>
        </div>

        {insightCard && <InsightContext card={insightCard} />}

        <ul className="divide-y divide-stone-100">
          {reviews.map((r) => (
            <li key={r.review_id} className="px-6 py-4">
              <div className="mb-1.5 flex items-center gap-2 text-xs text-stone-400">
                <span className="rounded bg-stone-100 px-1.5 py-0.5">{r.source}</span>
                <span className="text-amber-600">{'★'.repeat(r.rating)}</span>
                <span>{r.date?.slice(0, 10)}</span>
              </div>
              <p className="text-sm leading-relaxed text-stone-800">{r.text}</p>
              {r.subcategory_tags.length > 1 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {r.subcategory_tags
                    .filter((t) => t !== categoryId)
                    .map((t) => (
                      <span
                        key={t}
                        className="rounded-full bg-stone-100 px-2 py-0.5 text-[11px] text-stone-500"
                      >
                        {meta[t]?.name ?? t}
                      </span>
                    ))}
                </div>
              )}
            </li>
          ))}
          {reviews.length === 0 && (
            <li className="px-6 py-8 text-center text-sm text-stone-400">
              No sampled reviews for this category.
            </li>
          )}
        </ul>
      </aside>
    </>
  )
}
