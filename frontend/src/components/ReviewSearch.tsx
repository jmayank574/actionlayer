import { useEffect, useMemo, useState } from 'react'
import { Search, Loader2, X } from 'lucide-react'
import { loadAllReviews } from '../lib/data'
import type { AllReviewsEntry, CategoryMetaFile } from '../types'

const RESULTS_CAP = 50

type SourceFilter = 'all' | 'google_play' | 'app_store'

function matches(review: AllReviewsEntry, terms: string[], source: SourceFilter): boolean {
  if (source !== 'all' && review.source !== source) return false
  if (terms.length === 0) return true
  const haystack = review.text.toLowerCase()
  return terms.every((t) => haystack.includes(t))
}

function ResultRow({ review, meta }: { review: AllReviewsEntry; meta: CategoryMetaFile }) {
  return (
    <div className="border-b border-stone-100 px-5 py-4 last:border-b-0">
      <div className="flex items-center gap-2 text-xs text-stone-400">
        <span className="font-medium text-stone-600">{'★'.repeat(review.rating ?? 0)}</span>
        <span>{review.date?.slice(0, 10)}</span>
        <span>·</span>
        <span>{review.source === 'google_play' ? 'Google Play' : 'App Store'}</span>
      </div>
      <p className="mt-1.5 text-sm text-stone-700 leading-relaxed">{review.text}</p>
      {review.subcategory_tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {review.subcategory_tags.map((tag) => (
            <span key={tag} className="rounded-full bg-stone-100 px-2 py-0.5 text-[11px] text-stone-500">
              {meta[tag]?.name ?? tag}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ReviewSearch({
  dataSource,
  meta,
  onQueryActiveChange,
}: {
  dataSource: string
  meta: CategoryMetaFile
  onQueryActiveChange: (active: boolean) => void
}) {
  const [query, setQuery] = useState('')
  const [source, setSource] = useState<SourceFilter>('all')
  const [reviews, setReviews] = useState<AllReviewsEntry[] | null>(null)
  const [loading, setLoading] = useState(false)

  const queryActive = query.trim().length > 0

  useEffect(() => {
    onQueryActiveChange(queryActive)
  }, [queryActive, onQueryActiveChange])

  useEffect(() => {
    if (!queryActive || reviews || loading) return
    setLoading(true)
    loadAllReviews(dataSource).then((data) => {
      setReviews(data)
      setLoading(false)
    })
  }, [queryActive, reviews, loading, dataSource])

  const terms = useMemo(
    () => query.toLowerCase().split(/\s+/).map((t) => t.trim()).filter(Boolean),
    [query],
  )

  const results = useMemo(() => {
    if (!reviews || !queryActive) return []
    const out: AllReviewsEntry[] = []
    for (const r of reviews) {
      if (matches(r, terms, source)) out.push(r)
      if (out.length >= RESULTS_CAP) break
    }
    return out
  }, [reviews, terms, source, queryActive])

  return (
    <div>
      <div className="flex items-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-2.5 shadow-sm">
        <Search size={16} className="shrink-0 text-stone-400" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search all reviews — e.g. &ldquo;battery drains fast&rdquo;"
          className="flex-1 bg-transparent text-sm text-stone-800 placeholder:text-stone-400 focus:outline-none"
        />
        {queryActive && (
          <button onClick={() => setQuery('')} className="shrink-0 text-stone-400 hover:text-stone-700">
            <X size={15} />
          </button>
        )}
        <select
          value={source}
          onChange={(e) => setSource(e.target.value as SourceFilter)}
          className="shrink-0 rounded border border-stone-200 bg-white px-2 py-1 text-xs text-stone-600"
        >
          <option value="all">All sources</option>
          <option value="google_play">Google Play</option>
          <option value="app_store">App Store</option>
        </select>
      </div>

      {queryActive && (
        <div className="mt-4 rounded-2xl border border-stone-200 bg-white overflow-hidden">
          <div className="border-b border-stone-100 bg-stone-50/70 px-5 py-2.5 text-xs text-stone-500">
            {loading
              ? 'Searching…'
              : `${results.length}${results.length === RESULTS_CAP ? '+' : ''} match${results.length === 1 ? '' : 'es'}${reviews ? ` out of ${reviews.length.toLocaleString()} reviews` : ''}`}
          </div>
          {loading && (
            <div className="flex items-center justify-center gap-2 px-5 py-10 text-sm text-stone-400">
              <Loader2 size={15} className="animate-spin" /> Loading review corpus…
            </div>
          )}
          {!loading && results.length === 0 && (
            <p className="px-5 py-10 text-center text-sm text-stone-400">No matching reviews.</p>
          )}
          {!loading && results.length > 0 && (
            <div className="max-h-[600px] overflow-y-auto">
              {results.map((r) => (
                <ResultRow key={r.review_id} review={r} meta={meta} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
