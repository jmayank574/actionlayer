// Static-JSON data access. No backend server -- everything under public/data/
// is pre-computed by backend/export_dashboard_data.py and fetched as-is.
// Simple in-memory cache per URL so navigating between pages doesn't re-fetch.

import type {
  CategoryMetaFile,
  InsightFeedFile,
  ProductsFile,
  ReviewSamplesFile,
  SnapshotFile,
  TrendsTimeseriesFile,
  TrendVerdictsFile,
} from '../types'

const cache = new Map<string, Promise<unknown>>()

function getJSON<T>(url: string): Promise<T> {
  if (!cache.has(url)) {
    cache.set(
      url,
      fetch(url).then((res) => {
        if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`)
        return res.json() as Promise<T>
      }),
    )
  }
  return cache.get(url) as Promise<T>
}

export function loadProducts(): Promise<ProductsFile> {
  return getJSON<ProductsFile>('/data/products.json')
}

export function loadSnapshot(dataSource: string): Promise<SnapshotFile> {
  return getJSON<SnapshotFile>(`/data/${dataSource}/snapshot.json`)
}

export function loadTrendsTimeseries(dataSource: string): Promise<TrendsTimeseriesFile> {
  return getJSON<TrendsTimeseriesFile>(`/data/${dataSource}/trends_timeseries.json`)
}

export function loadTrendVerdicts(dataSource: string): Promise<TrendVerdictsFile> {
  return getJSON<TrendVerdictsFile>(`/data/${dataSource}/trend_verdicts.json`)
}

export function loadReviewSamples(dataSource: string): Promise<ReviewSamplesFile> {
  return getJSON<ReviewSamplesFile>(`/data/${dataSource}/review_samples.json`)
}

export function loadCategoryMeta(dataSource: string): Promise<CategoryMetaFile> {
  return getJSON<CategoryMetaFile>(`/data/${dataSource}/category_meta.json`)
}

export function loadInsightFeed(dataSource: string): Promise<InsightFeedFile> {
  return getJSON<InsightFeedFile>(`/data/${dataSource}/insight_feed.json`)
}

// Groups products by category, deriving the Category -> Product tree from
// the flat products.json list. Adding a second product to that file (even
// in an existing category, or a brand new one) requires no code change here.
export async function loadCategoryTree() {
  const { products } = await loadProducts()
  const byCategory = new Map<string, typeof products>()
  for (const p of products) {
    const list = byCategory.get(p.category) ?? []
    list.push(p)
    byCategory.set(p.category, list)
  }
  return Array.from(byCategory.entries()).map(([category, categoryProducts]) => ({
    category,
    products: categoryProducts,
  }))
}
