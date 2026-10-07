import TrendChart from './TrendChart'
import type { InsightCard as InsightCardType, TrendPoint } from '../types'
import { SCOPE_LABEL } from '../lib/trends'
import { SEVERITY } from '../lib/severity'

function QuoteBlock({ quote }: { quote: { source: string; rating: number; date: string; text: string } }) {
  return (
    <p className="text-[13.5px] text-stone-600 leading-relaxed">
      “{quote.text}”{' '}
      <span className="whitespace-nowrap text-stone-400">
        — {quote.date?.slice(5, 10).replace('-', '/')} · {quote.source === 'google_play' ? 'Play' : 'App Store'}
      </span>
    </p>
  )
}

export default function InsightCard({
  card,
  sparkline,
  scope,
  onBrowseCategory,
}: {
  card: InsightCardType
  sparkline: TrendPoint[]
  scope: string
  onBrowseCategory: (categoryId: string) => void
}) {
  const severity = SEVERITY[card.status]
  const sign = (card.pp_delta ?? 0) >= 0 ? '+' : ''

  return (
    <div className="rounded-2xl bg-white p-6 shadow-[0_1px_2px_rgba(23,20,15,0.06),0_8px_24px_rgba(23,20,15,0.04)]">
      <div className="flex items-center gap-2">
        <span className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-[11px] font-semibold ${severity.badgeClass}`}>
          <span aria-hidden>{severity.icon}</span>
          {severity.label}
        </span>
        <h3 className="font-serif text-lg font-semibold text-stone-900 leading-snug">
          {card.category_name}
        </h3>
      </div>

      {/* Lead with the scannable numbers before the prose -- same figures
          the narrative paragraph below spells out in full sentences, just
          readable in one glance first. */}
      <p className="mt-2 text-sm font-medium tabular-nums text-stone-700">
        {card.recent_rate_pct.toFixed(1)}% of reviews
        {card.ratio != null && <> · {card.ratio.toFixed(1)}x baseline</>}
        {card.pp_delta != null && (
          <> · <span className={severity.textClass}>{sign}{card.pp_delta.toFixed(1)}pp</span></>
        )}
        {' · '}{card.recent_count.toLocaleString()} mentions
      </p>

      <p className="mt-3 rounded-lg bg-stone-50 px-3 py-2 text-[13px] font-medium text-stone-700">
        → {card.recommended_action}
      </p>

      <p className="mt-2.5 text-[13.5px] text-stone-500 leading-relaxed">{card.narrative}</p>

      <div className="mt-5 grid grid-cols-1 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] gap-6 items-start">
        <div>
          <p className="mb-1 text-[11px] text-stone-400">{SCOPE_LABEL[scope] ?? scope}</p>
          {/* Chart color is intentionally constant across every card here --
              it tracks "this is the thing being measured," not the verdict.
              The badge above is the one place direction/verdict lives; having
              the chart color echo it too was redundant and, worse, sometimes
              contradicted the badge once sentiment could disagree with rate
              direction (see ai_coach: rate rising, badge amber, chart would
              have been rust -- all telling slightly different stories). */}
          <TrendChart data={sparkline} status="unknown" hideCaption />
        </div>
        <div className="space-y-4">
          {card.quotes.map((q) => (
            <QuoteBlock key={q.review_id} quote={q} />
          ))}
        </div>
      </div>

      <button
        onClick={() => onBrowseCategory(card.category_id)}
        className="mt-5 rounded-full bg-rust-500 px-4 py-2 text-sm font-medium text-white hover:bg-rust-600 transition-colors"
      >
        See all mentions →
      </button>
    </div>
  )
}
