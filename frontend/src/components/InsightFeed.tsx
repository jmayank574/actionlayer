import InsightCard from './InsightCard'
import WatchZone from './WatchZone'
import type { InsightFeedFile, TrendsTimeseriesFile } from '../types'

export default function InsightFeed({
  feed,
  timeseries,
  onBrowseCategory,
}: {
  feed: InsightFeedFile
  timeseries: TrendsTimeseriesFile
  onBrowseCategory: (categoryId: string) => void
}) {
  const zoneACards = feed.zone_a_ids.map((id) => feed.cards[id]).filter(Boolean)
  const watchCards = feed.watch_zone_ids.map((id) => feed.cards[id]).filter(Boolean)

  return (
    <div className="space-y-8">
      <div
        className="grid grid-cols-1 lg:grid-cols-2 gap-5"
        title={`Ranked by ${feed.priority_score_formula.split(' -- ')[0]}, min. ${feed.zone_a_min_volume} recent mentions. Data: ${feed.window_label}, both sources combined.`}
      >
        {zoneACards.map((card) => (
          <InsightCard
            key={card.category_id}
            card={card}
            sparkline={timeseries[feed.scope]?.[card.category_id] ?? []}
            scope={feed.scope}
            onBrowseCategory={onBrowseCategory}
          />
        ))}
      </div>
      {zoneACards.length === 0 && (
        <p className="text-stone-400 text-sm">No categories clear the priority bar this period.</p>
      )}

      <WatchZone cards={watchCards} scope={feed.scope} onBrowseCategory={onBrowseCategory} />
    </div>
  )
}
