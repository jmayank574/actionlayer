import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  loadCategoryMeta,
  loadCategoryTree,
  loadInsightFeed,
  loadReviewSamples,
  loadSnapshot,
  loadTrendsTimeseries,
  loadTrendVerdicts,
} from '../lib/data'
import { slugify } from '../lib/slug'
import CategoryBreakdown from '../components/CategoryBreakdown'
import BrokenBasicsCallout from '../components/BrokenBasicsCallout'
import TrendView from '../components/TrendView'
import WatchCategoryPanel from '../components/WatchCategoryPanel'
import ReviewDrawer from '../components/ReviewDrawer'
import InsightFeed from '../components/InsightFeed'
import type {
  CategoryMetaFile,
  InsightFeedFile,
  ProductConfig,
  ReviewSamplesFile,
  SnapshotFile,
  TrendsTimeseriesFile,
  TrendVerdictsFile,
} from '../types'

type Tab = 'insights' | 'explore'

export default function ProductDashboard() {
  const { categorySlug, productId } = useParams()
  const [product, setProduct] = useState<ProductConfig | null | undefined>(undefined)
  const [snapshot, setSnapshot] = useState<SnapshotFile | null>(null)
  const [timeseries, setTimeseries] = useState<TrendsTimeseriesFile | null>(null)
  const [verdicts, setVerdicts] = useState<TrendVerdictsFile | null>(null)
  const [samples, setSamples] = useState<ReviewSamplesFile | null>(null)
  const [meta, setMeta] = useState<CategoryMetaFile | null>(null)
  const [insightFeed, setInsightFeed] = useState<InsightFeedFile | null>(null)
  const [drawerCategory, setDrawerCategory] = useState<string | null>(null)
  const [focusedTrendCategory, setFocusedTrendCategory] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('insights')

  useEffect(() => {
    loadCategoryTree().then((groups) => {
      const match = groups
        .find((g) => slugify(g.category) === categorySlug)
        ?.products.find((p) => p.id === productId)
      setProduct(match ?? null)
    })
  }, [categorySlug, productId])

  useEffect(() => {
    if (!product) return
    loadSnapshot(product.data_source).then(setSnapshot)
    loadTrendsTimeseries(product.data_source).then(setTimeseries)
    loadTrendVerdicts(product.data_source).then(setVerdicts)
    loadReviewSamples(product.data_source).then(setSamples)
    loadCategoryMeta(product.data_source).then(setMeta)
    loadInsightFeed(product.data_source).then(setInsightFeed)
  }, [product])

  if (product === undefined) return <p className="text-stone-500">Loading…</p>
  if (product === null) return <p className="text-rust-600">Unknown product.</p>

  const loading = !snapshot || !timeseries || !verdicts || !samples || !meta || !insightFeed

  function focusTrend(categoryId: string) {
    setFocusedTrendCategory(categoryId)
    setTab('explore')
    requestAnimationFrame(() =>
      document.getElementById('trend-view')?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link
            to={`/category/${categorySlug}`}
            className="text-sm text-stone-500 hover:text-stone-800"
          >
            ← {product.category}
          </Link>
          <h1 className="font-serif text-[28px] font-semibold text-stone-900 mt-1">
            {tab === 'insights' ? `Insights found by ${product.product}` : `${product.product}: all categories`}
          </h1>
        </div>
        {!loading && (
          <div className="flex gap-1 rounded-full bg-stone-200/60 p-1">
            <button
              onClick={() => setTab('insights')}
              className={`rounded-full px-4 py-1.5 text-[13px] font-medium transition-colors ${
                tab === 'insights' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Insights
            </button>
            <button
              onClick={() => setTab('explore')}
              className={`rounded-full px-4 py-1.5 text-[13px] font-medium transition-colors ${
                tab === 'explore' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Explore all
            </button>
          </div>
        )}
      </div>

      {loading && <p className="text-stone-500">Loading dashboard data…</p>}

      {!loading && tab === 'insights' && (
        <InsightFeed
          feed={insightFeed!}
          timeseries={timeseries!}
          onBrowseCategory={setDrawerCategory}
        />
      )}

      {!loading && tab === 'explore' && (
        <div className="space-y-8">
          <BrokenBasicsCallout parents={snapshot!.parents} onSelectCategory={setDrawerCategory} />

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-3">
              Category &amp; subcategory breakdown
            </h2>
            <CategoryBreakdown
              parents={snapshot!.parents}
              otherUngrouped={snapshot!.other_ungrouped}
              totalReviews={snapshot!.total_reviews}
              verdicts={verdicts!}
              onSelectCategory={setDrawerCategory}
              onFocusTrend={focusTrend}
            />
          </section>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-3">
              Watch categories
            </h2>
            <WatchCategoryPanel
              watchParents={snapshot!.parents.filter((p) => p.watch_category)}
              verdicts={verdicts!}
              onSelectCategory={setDrawerCategory}
            />
          </section>

          <section id="trend-view">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-3">
              Rising &amp; falling
            </h2>
            <TrendView
              verdicts={verdicts!}
              timeseries={timeseries!}
              focusedCategory={focusedTrendCategory}
              onFocusCategory={setFocusedTrendCategory}
              onSelectCategory={setDrawerCategory}
            />
          </section>
        </div>
      )}

      {meta && samples && (
        <ReviewDrawer
          categoryId={drawerCategory}
          meta={meta}
          samples={samples}
          insightCard={drawerCategory ? insightFeed?.cards[drawerCategory] : undefined}
          onClose={() => setDrawerCategory(null)}
        />
      )}
    </div>
  )
}
