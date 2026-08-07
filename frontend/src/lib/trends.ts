import type { TrendVerdict } from '../types'

export function findVerdict(
  verdicts: TrendVerdict[],
  scope: string,
  categoryId: string,
): TrendVerdict | undefined {
  return verdicts.find((v) => v.scope === scope && v.category_id === categoryId)
}

export type TrendStatus = 'rising' | 'falling' | 'stable' | 'unknown'

export function statusFor(verdict: TrendVerdict | undefined): TrendStatus {
  if (!verdict) return 'unknown'
  if (verdict.flagged_spike) return 'rising'
  if (verdict.flagged_decline) return 'falling'
  if (verdict.verdict === 'stable') return 'stable'
  return 'unknown' // insufficient_recent_occurrences / insufficient_baseline_volume
}

// "Broken basics" (things not working) vs. "Feature Requests" (asks for new
// capability) -- the parent-category ids that make up each side of the
// framing from Fix 3. Ids only, never numbers: every percentage shown is
// computed live from whatever snapshot.json currently contains.
export const BROKEN_BASICS_IDS = ['sync_connectivity', 'app_stability', 'ui_ux']
export const FEATURE_REQUEST_ID = 'feature_requests'

// Every insight-feed number must disclose which source scope it's computed
// from -- combined_overlap is restricted to Nov 2025 onward (app_store's
// real history), while a single-source scope can span years. Mislabeling
// this (or omitting it) is exactly the kind of thing that gets misquoted
// later, so this label is not decorative.
export const SCOPE_LABEL: Record<string, string> = {
  google_play: 'Google Play',
  app_store: 'App Store',
  combined_overlap: 'Combined · Nov 2025+',
}
