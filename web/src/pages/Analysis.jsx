import { useState, useEffect } from 'react'

export default function Analysis() {
  const [categories, setCategories] = useState([])
  const [merchants, setMerchants] = useState([])
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/analysis/categories').then(r => r.json()),
      fetch('/api/analysis/merchants?limit=10').then(r => r.json()),
      fetch('/api/analysis/trends?months=6').then(r => r.json())
    ])
      .then(([cats, merch, trend]) => {
        setCategories(cats)
        setMerchants(merch)
        setTrends(trend)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Spending Analysis</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <h3 className="text-lg font-semibold mb-4">By Category</h3>
          <div className="space-y-3">
            {categories.filter(c => c.total_amount > 0).map(cat => (
              <div key={cat.category} className="flex items-center justify-between">
                <span className="text-gray-700">{cat.category}</span>
                <span className="font-medium">TWD {cat.total_amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Merchants */}
        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <h3 className="text-lg font-semibold mb-4">Top Merchants</h3>
          <div className="space-y-3">
            {merchants.map((m, i) => (
              <div key={m.merchant} className="flex items-center justify-between">
                <span className="text-gray-700">
                  <span className="text-gray-400 mr-2">{i + 1}.</span>
                  {m.merchant.slice(0, 30)}
                </span>
                <span className="font-medium">TWD {m.total_amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monthly Trends */}
      <div className="bg-white rounded-xl shadow-sm p-6 border">
        <h3 className="text-lg font-semibold mb-4">Monthly Trends</h3>
        <div className="grid grid-cols-6 gap-4">
          {trends.map(t => (
            <div key={`${t.year}-${t.month}`} className="text-center">
              <div className="text-sm text-gray-500">{t.year}/{t.month}</div>
              <div className="font-bold text-lg">TWD {(t.total_amount / 1000).toFixed(0)}K</div>
              <div className="text-xs text-gray-400">{t.transaction_count} txs</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
