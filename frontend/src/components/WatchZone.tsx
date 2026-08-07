import { SCOPE_LABEL } from '../lib/trends'
import type { InsightCard, InsightStatus } from '../types'

const DIRECTION: Record<InsightStatus, string> = {
  needs_attention: '▲',
  improving: '▼',
  watching: '●',
  stable: '●',
}

export default function WatchZone({
  cards,
  scope,
  onBrowseCategory,
}: {
  cards: InsightCard[]
  scope: string
  onBrowseCategory: (categoryId: string) => void
}) {
  if (cards.length === 0) return null

  return (
    <div>
      <h2
        className="mb-3 font-serif text-sm font-medium text-stone-500"
        title="Always shown, regardless of volume or rank — stakes, not size, put these here."
      >
        Watch Categories
      </h2>
      <div className="rounded-2xl border border-amber-200/70 bg-amber-50/40">
        <ul className="divide-y divide-amber-200/40">
          {cards.map((card) => {
            const sign = (card.pp_delta ?? 0) >= 0 ? '+' : ''
            return (
              <li key={card.category_id} className="flex items-center gap-3 px-5 py-3">
                <span className="w-4 text-center text-amber-600" aria-hidden>
                  {DIRECTION[card.status]}
                </span>
                <button
                  onClick={() => onBrowseCategory(card.category_id)}
                  className="flex-1 text-left text-sm font-medium text-stone-800 hover:underline"
                >
                  {card.category_name}
                </button>
                <span className="hidden md:inline text-[11px] text-stone-400">
                  {SCOPE_LABEL[scope] ?? scope}
                </span>
                <span className="hidden sm:inline text-xs text-stone-500">
                  {card.recent_count} mentions
                </span>
                <span className="w-20 text-right text-sm tabular-nums font-medium text-stone-700">
                  {card.recent_rate_pct.toFixed(1)}%
                </span>
                <span className="w-16 text-right text-xs tabular-nums text-stone-400">
                  {sign}
                  {card.pp_delta?.toFixed(1) ?? '–'}pp
                </span>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
