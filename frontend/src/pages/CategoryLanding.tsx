import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { loadCategoryTree } from '../lib/data'
import { slugify } from '../lib/slug'

interface CategoryGroup {
  category: string
  products: { id: string; product: string }[]
}

export default function CategoryLanding() {
  const [groups, setGroups] = useState<CategoryGroup[] | null>(null)

  useEffect(() => {
    loadCategoryTree().then(setGroups)
  }, [])

  if (!groups) return <p className="text-stone-500">Loading categories…</p>

  return (
    <div>
      <h1 className="font-serif text-3xl font-medium text-stone-900 mb-2">Categories</h1>
      <p className="text-stone-500 mb-10 max-w-xl">
        One category tracked today. Adding another product or category is additive to{' '}
        <code className="rounded bg-stone-100 px-1.5 py-0.5 text-[13px]">
          public/data/products.json
        </code>{' '}
        — no schema change.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {groups.map((g) => (
          <Link
            key={g.category}
            to={`/category/${slugify(g.category)}`}
            className="rounded-2xl border border-stone-200 bg-white p-6 hover:border-stone-400 transition-colors"
          >
            <h2 className="font-serif text-xl font-medium text-stone-900">{g.category}</h2>
            <p className="text-sm text-stone-500 mt-1.5">
              {g.products.length} product{g.products.length === 1 ? '' : 's'} —{' '}
              {g.products.map((p) => p.product).join(', ')}
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}
