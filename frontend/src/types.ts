// Mirrors the JSON shapes written by backend/export_dashboard_data.py.
// If the export script's output shape changes, these types (and the data/
// under public/data/) need to move together -- there is no runtime schema
// validation yet (see README "stubbed" list).

export interface ProductConfig {
  id: string
  category: string
  product: string
  data_source: string
}

export interface ProductsFile {
  products: ProductConfig[]
}

export interface SubcategorySnapshot {
  id: string
  name: string
  count: number
  rate_pct: number | null
  watch_category: boolean
}

export interface ParentSnapshot {
  id: string
  name: string
  count: number
  rate_pct: number | null
  watch_category: boolean
  watch_reason: string | null
  subcategories: SubcategorySnapshot[]
}

export interface SnapshotFile {
  product_id: string
  total_reviews: number
  other_ungrouped: { count: number; rate_pct: number | null }
  parents: ParentSnapshot[]
}

export interface TrendPoint {
  period: string
  period_type: 'month' | 'multi_month'
  period_start: string
  period_end: string
  rate_pct: number | null
  tag_count: number
  total_reviews: number
  adequate_volume: boolean
  // The current calendar month, still in progress -- real data, shown as its
  // own point, but excluded from spike/decline verdicts until complete.
  is_current_partial: boolean
  in_recent_window: boolean
  flagged_spike: boolean
  flagged_decline: boolean
}

// scope ("google_play" | "app_store") -> category_id -> chronological points
export type TrendsTimeseriesFile = Record<string, Record<string, TrendPoint[]>>

export type TrendScope = 'google_play' | 'app_store' | 'combined_overlap'

export interface TrendVerdict {
  scope: TrendScope
  level: 'parent' | 'subcategory'
  category_id: string
  category_name: string
  watch_category: boolean
  recent_count: number
  recent_total: number
  recent_rate_pct: number | null
  baseline_count: number
  baseline_total: number
  baseline_rate_pct: number | null
  pp_delta: number | null
  ratio: number | null
  verdict:
    | 'spike'
    | 'decline'
    | 'stable'
    | 'emerging_new_category'
    | 'insufficient_recent_occurrences'
    | 'insufficient_baseline_volume'
  flagged_spike: boolean
  flagged_decline: boolean
  emerging: boolean
}

export type TrendVerdictsFile = TrendVerdict[]

export interface ReviewSample {
  review_id: string
  source: 'google_play' | 'app_store'
  rating: number
  date: string
  text: string
  subcategory_tags: string[]
}

// category_id -> up to REVIEW_SAMPLE_CAP most-recent reviews
export type ReviewSamplesFile = Record<string, ReviewSample[]>

export interface InsightQuote {
  review_id: string
  source: 'google_play' | 'app_store'
  rating: number
  date: string
  text: string
}

export type InsightStatus = 'watching' | 'needs_attention' | 'improving' | 'stable'

export interface InsightDriver {
  category_id: string
  name: string
  recent_rate_pct: number | null
  baseline_rate_pct: number | null
  pp_delta: number | null
  verdict: string
  quote: InsightQuote | null
}

export interface InsightCard {
  category_id: string
  category_name: string
  watch_category: boolean
  watch_reason: string | null
  status: InsightStatus
  title: string
  narrative: string
  recent_rate_pct: number
  baseline_rate_pct: number
  pp_delta: number | null
  ratio: number | null
  recent_count: number
  recent_total: number
  baseline_count: number
  baseline_total: number
  subcategory_contribution_sum_pct: number
  multi_label_note: string | null
  top_drivers: InsightDriver[]
  quotes: InsightQuote[]
  priority_score: number
}

export interface InsightFeedFile {
  scope: string
  window_label: string
  window_start: string
  window_end: string
  priority_score_formula: string
  zone_a_min_volume: number
  zone_a_min_volume_reasoning: string
  cards: Record<string, InsightCard>
  zone_a_ids: string[]
  watch_zone_ids: string[]
}

export interface CategoryMetaEntry {
  name: string
  level: 'parent' | 'subcategory'
  parent_id: string | null
  watch_category: boolean
  watch_reason: string | null
}

export type CategoryMetaFile = Record<string, CategoryMetaEntry>
