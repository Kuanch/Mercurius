import { useState, useEffect } from 'react'
import { ArrowUp, ArrowDown, DollarSign, CreditCard } from 'lucide-react'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/analysis/monthly')
      .then(res => res.json())
      .then(data => {
        setSummary(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Spending</p>
              <p className="text-2xl font-bold text-gray-900">
                TWD {summary?.total_amount?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <DollarSign className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary?.transaction_count || 0}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <CreditCard className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Period</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary?.year}/{summary?.month}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <ArrowUp className="text-purple-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6 border">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="flex gap-4">
          <button
            onClick={() => fetch('/api/bills/sync', { method: 'POST' })}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Sync Bills from Gmail
          </button>
        </div>
      </div>
    </div>
  )
}
