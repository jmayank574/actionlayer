import TrendChart from './TrendChart'
import type { InsightCard as InsightCardType, InsightStatus, TrendPoint } from '../types'
import { SCOPE_LABEL, type TrendStatus } from '../lib/trends'

const STATUS_STYLE: Record<InsightStatus, { label: string; badge: string }> = {
  needs_attention: { label: 'Needs Attention', badge: 'bg-rust-500 text-white' },
  improving: { label: 'Going Well', badge: 'bg-sage-500 text-white' },
  watching: { label: 'Watching', badge: 'bg-amber-500 text-white' },
  stable: { label: 'Stable', badge: 'bg-stone-400 text-white' },
}

const CHART_STATUS: Record<InsightStatus, TrendStatus> = {
  needs_attention: 'rising',
  improving: 'falling',
  watching: 'unknown',
  stable: 'stable',
}

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
  const style = STATUS_STYLE[card.status]

  return (
    <div className="rounded-2xl bg-white p-6 shadow-[0_1px_2px_rgba(23,20,15,0.06),0_8px_24px_rgba(23,20,15,0.04)]">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-serif text-lg font-semibold text-stone-900 leading-snug pr-2">
          {card.title}
        </h3>
        <span className={`shrink-0 rounded-full px-3 py-1 text-[11px] font-semibold ${style.badge}`}>
          {style.label}
        </span>
      </div>

      <p className="mt-2.5 text-[13.5px] text-stone-500 leading-relaxed">{card.narrative}</p>

      <div className="mt-5 grid grid-cols-1 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] gap-6 items-start">
        <div>
          <p className="mb-1 text-[11px] text-stone-400">{SCOPE_LABEL[scope] ?? scope}</p>
          <TrendChart data={sparkline} status={CHART_STATUS[card.status]} />
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
