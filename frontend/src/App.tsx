import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import CategoryLanding from './pages/CategoryLanding'
import CategoryPage from './pages/CategoryPage'
import ProductDashboard from './pages/ProductDashboard'

export default function App() {
  return (
    <div className="flex h-screen bg-cream">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-8 py-10 sm:px-12">
        <div className="mx-auto max-w-6xl">
          <Routes>
            <Route path="/" element={<CategoryLanding />} />
            <Route path="/category/:categorySlug" element={<CategoryPage />} />
            <Route
              path="/category/:categorySlug/product/:productId"
              element={<ProductDashboard />}
            />
          </Routes>
        </div>
      </main>
    </div>
  )
}
