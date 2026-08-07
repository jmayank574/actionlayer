import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { loadCategoryTree } from '../lib/data'
import { slugify } from '../lib/slug'
import type { ProductConfig } from '../types'

export default function CategoryPage() {
  const { categorySlug } = useParams()
  const [category, setCategory] = useState<string | null>(null)
  const [products, setProducts] = useState<ProductConfig[] | null>(null)

  useEffect(() => {
    loadCategoryTree().then((groups) => {
      const match = groups.find((g) => slugify(g.category) === categorySlug)
      setCategory(match?.category ?? null)
      setProducts(match?.products ?? [])
    })
  }, [categorySlug])

  if (!products) return <p className="text-stone-500">Loading…</p>
  if (!category) return <p className="text-rust-600">Unknown category.</p>

  return (
    <div>
      <Link to="/" className="text-sm text-stone-500 hover:text-stone-800">
        ← Categories
      </Link>
      <h1 className="font-serif text-3xl font-medium text-stone-900 mt-2 mb-10">{category}</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {products.map((p) => (
          <Link
            key={p.id}
            to={`/category/${categorySlug}/product/${p.id}`}
            className="rounded-2xl border border-stone-200 bg-white p-6 hover:border-stone-400 transition-colors"
          >
            <h2 className="font-serif text-xl font-medium text-stone-900">{p.product}</h2>
            <p className="text-sm text-stone-500 mt-1.5">Open dashboard →</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
