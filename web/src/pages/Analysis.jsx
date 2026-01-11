import { useState, useEffect, useMemo } from 'react'
import { PieChart, TrendingUp, Store, Calendar, ChevronDown } from 'lucide-react'

// Category colors for visual representation
const CATEGORY_COLORS = {
  'Food & Dining': { bg: 'bg-orange-500', text: 'text-orange-400' },
  'Shopping': { bg: 'bg-rose-500', text: 'text-rose-400' },
  'Transport': { bg: 'bg-blue-500', text: 'text-blue-400' },
  'Entertainment': { bg: 'bg-purple-500', text: 'text-purple-400' },
  'Groceries': { bg: 'bg-emerald-500', text: 'text-emerald-400' },
  'Bills & Utilities': { bg: 'bg-cyan-500', text: 'text-cyan-400' },
  'Healthcare': { bg: 'bg-pink-500', text: 'text-pink-400' },
  'Travel': { bg: 'bg-indigo-500', text: 'text-indigo-400' },
  'Other': { bg: 'bg-gray-500', text: 'text-gray-400' },
}

function ProgressBar({ value, max, color = 'bg-primary' }) {
  const percentage = max > 0 ? (value / max) * 100 : 0
  return (
    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
      <div
        className={`h-full ${color} transition-all duration-500`}
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
  )
}

function StatCard({ icon: Icon, title, value, subtitle, iconColor = 'text-primary' }) {
  return (
    <div className="flex flex-col gap-1 rounded-xl p-6 bg-surface-dark border border-border-dark">
      <div className="flex justify-between items-start">
        <p className="text-gray-400 text-sm font-semibold uppercase tracking-wider">{title}</p>
        <span className={`${iconColor} bg-white/5 p-1.5 rounded-lg`}>
          <Icon size={20} />
        </span>
      </div>
      <p className="text-white text-2xl font-bold tracking-tight mt-2">{value}</p>
      {subtitle && (
        <p className="text-gray-400 text-xs">{subtitle}</p>
      )}
    </div>
  )
}

export default function Analysis() {
  const [categories, setCategories] = useState([])
  const [merchants, setMerchants] = useState([])
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())

  useEffect(() => {
    Promise.all([
      fetch(`/api/analysis/categories?year=${selectedYear}`).then(r => r.json()),
      fetch('/api/analysis/merchants?limit=10').then(r => r.json()),
      fetch('/api/analysis/trends?months=12').then(r => r.json())
    ])
      .then(([cats, merch, trend]) => {
        setCategories(cats)
        setMerchants(merch)
        setTrends(trend)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [selectedYear])

  // Calculate stats
  const stats = useMemo(() => {
    const totalSpending = categories.reduce((sum, c) => sum + (c.total_amount || 0), 0)
    const avgMonthly = trends.length > 0
      ? trends.reduce((sum, t) => sum + (t.total_amount || 0), 0) / trends.length
      : 0
    const topCategory = categories.length > 0
      ? categories.reduce((max, c) => c.total_amount > max.total_amount ? c : max, categories[0])
      : null
    return { totalSpending, avgMonthly, topCategory }
  }, [categories, trends])

  const maxCategoryAmount = useMemo(() => {
    return Math.max(...categories.map(c => c.total_amount || 0), 1)
  }, [categories])

  const maxMerchantAmount = useMemo(() => {
    return Math.max(...merchants.map(m => m.total_amount || 0), 1)
  }, [merchants])

  const maxTrendAmount = useMemo(() => {
    return Math.max(...trends.map(t => t.total_amount || 0), 1)
  }, [trends])

  // Generate year options
  const yearOptions = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="flex flex-col gap-3">
          <h2 className="text-3xl md:text-4xl font-black text-white tracking-tight">Spending Analysis</h2>
          <div className="relative w-fit">
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="appearance-none bg-transparent text-gray-400 text-base md:text-lg font-medium pr-8 pl-0 border-0 focus:ring-0 cursor-pointer focus:outline-none"
            >
              {yearOptions.map(year => (
                <option key={year} value={year} className="bg-surface-dark">
                  {year}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500" size={18} />
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          icon={PieChart}
          title="Total Spending"
          value={`TWD ${stats.totalSpending.toLocaleString()}`}
          subtitle={`${categories.length} categories`}
          iconColor="text-primary"
        />
        <StatCard
          icon={TrendingUp}
          title="Monthly Average"
          value={`TWD ${Math.round(stats.avgMonthly).toLocaleString()}`}
          subtitle={`Based on ${trends.length} months`}
          iconColor="text-emerald-400"
        />
        <StatCard
          icon={Store}
          title="Top Category"
          value={stats.topCategory?.category || 'N/A'}
          subtitle={stats.topCategory ? `TWD ${stats.topCategory.total_amount.toLocaleString()}` : ''}
          iconColor="text-purple-400"
        />
      </section>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-surface-dark rounded-xl border border-border-dark p-6">
          <div className="flex items-center gap-3 mb-6">
            <PieChart className="text-primary" size={24} />
            <h3 className="text-lg font-bold text-white">By Category</h3>
          </div>
          <div className="space-y-4">
            {categories
              .filter(c => c.total_amount > 0)
              .sort((a, b) => b.total_amount - a.total_amount)
              .slice(0, 8)
              .map(cat => {
                const colors = CATEGORY_COLORS[cat.category] || CATEGORY_COLORS['Other']
                const percentage = ((cat.total_amount / stats.totalSpending) * 100).toFixed(1)
                return (
                  <div key={cat.category} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`text-sm font-medium ${colors.text}`}>{cat.category}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-gray-500">{percentage}%</span>
                        <span className="text-sm text-white font-medium">
                          TWD {cat.total_amount.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <ProgressBar
                      value={cat.total_amount}
                      max={maxCategoryAmount}
                      color={colors.bg}
                    />
                  </div>
                )
              })}
            {categories.filter(c => c.total_amount > 0).length === 0 && (
              <p className="text-gray-400 text-center py-4">No spending data available</p>
            )}
          </div>
        </div>

        {/* Top Merchants */}
        <div className="bg-surface-dark rounded-xl border border-border-dark p-6">
          <div className="flex items-center gap-3 mb-6">
            <Store className="text-emerald-400" size={24} />
            <h3 className="text-lg font-bold text-white">Top Merchants</h3>
          </div>
          <div className="space-y-4">
            {merchants.slice(0, 8).map((m, index) => (
              <div key={m.merchant} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-xs text-gray-500 w-5">{index + 1}.</span>
                    <span className="text-sm text-gray-300 truncate" title={m.merchant}>
                      {m.merchant.slice(0, 30)}{m.merchant.length > 30 ? '...' : ''}
                    </span>
                  </div>
                  <span className="text-sm text-white font-medium whitespace-nowrap ml-4">
                    TWD {m.total_amount.toLocaleString()}
                  </span>
                </div>
                <ProgressBar
                  value={m.total_amount}
                  max={maxMerchantAmount}
                  color="bg-emerald-500"
                />
              </div>
            ))}
            {merchants.length === 0 && (
              <p className="text-gray-400 text-center py-4">No merchant data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Monthly Trends */}
      <div className="bg-surface-dark rounded-xl border border-border-dark p-6">
        <div className="flex items-center gap-3 mb-6">
          <Calendar className="text-purple-400" size={24} />
          <h3 className="text-lg font-bold text-white">Monthly Trends</h3>
        </div>

        {trends.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No trend data available</p>
        ) : (
          <div className="space-y-6">
            {/* Bar chart */}
            <div className="flex items-end gap-2 h-48 px-4">
              {trends.slice(-12).map((t, i) => {
                const height = maxTrendAmount > 0
                  ? (t.total_amount / maxTrendAmount) * 100
                  : 0
                return (
                  <div key={`${t.year}-${t.month}`} className="flex-1 flex flex-col items-center gap-2">
                    <div className="w-full flex flex-col items-center justify-end h-40">
                      <span className="text-xs text-gray-400 mb-1">
                        {(t.total_amount / 1000).toFixed(0)}K
                      </span>
                      <div
                        className="w-full max-w-8 bg-gradient-to-t from-primary to-primary/60 rounded-t transition-all duration-500"
                        style={{ height: `${height}%`, minHeight: height > 0 ? '4px' : '0' }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{t.month}/{String(t.year).slice(-2)}</span>
                  </div>
                )
              })}
            </div>

            {/* Summary stats */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border-dark">
              <div className="text-center">
                <p className="text-2xl font-bold text-white">
                  {trends.reduce((sum, t) => sum + t.transaction_count, 0)}
                </p>
                <p className="text-xs text-gray-400">Total Transactions</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-white">
                  TWD {Math.round(trends.reduce((sum, t) => sum + t.total_amount, 0) / trends.length / 1000)}K
                </p>
                <p className="text-xs text-gray-400">Avg. Monthly</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-white">
                  TWD {Math.round(Math.max(...trends.map(t => t.total_amount)) / 1000)}K
                </p>
                <p className="text-xs text-gray-400">Peak Month</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
