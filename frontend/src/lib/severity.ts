import type { InsightStatus } from '../types'

// Single severity vocabulary shared by every component that shows a status
// badge (InsightCard, WatchZone, and anywhere else that renders one) -- the
// dashboard previously used a colored pill in one place and an unrelated
// direction arrow/dot in another, which meant re-learning the visual code
// twice on the same page. Icon + label together, not color alone (a
// colorblind-safe pattern), and the label is the one a reader can say in a
// sentence, not a raw technical status.
export const SEVERITY: Record<InsightStatus, { icon: string; label: string; badgeClass: string; textClass: string }> = {
  needs_attention: { icon: '⚠', label: 'Needs Attention', badgeClass: 'bg-rust-500 text-white', textClass: 'text-rust-600' },
  watching: { icon: '●', label: 'Watching', badgeClass: 'bg-amber-500 text-white', textClass: 'text-amber-600' },
  improving: { icon: '✓', label: 'Going Well', badgeClass: 'bg-sage-500 text-white', textClass: 'text-sage-600' },
  stable: { icon: '–', label: 'Stable', badgeClass: 'bg-stone-400 text-white', textClass: 'text-stone-500' },
}
