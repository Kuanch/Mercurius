import { useState, useEffect, useMemo } from 'react'
import { Search, Filter, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react'

// Category badge styling
const CATEGORY_STYLES = {
  'Food & Dining': 'bg-orange-900/40 text-orange-200 border-orange-700/30',
  'Shopping': 'bg-rose-900/40 text-rose-200 border-rose-700/30',
  'Transport': 'bg-blue-900/40 text-blue-200 border-blue-700/30',
  'Entertainment': 'bg-purple-900/40 text-purple-200 border-purple-700/30',
  'Groceries': 'bg-emerald-900/40 text-emerald-200 border-emerald-700/30',
  'Bills & Utilities': 'bg-cyan-900/40 text-cyan-200 border-cyan-700/30',
  'Healthcare': 'bg-pink-900/40 text-pink-200 border-pink-700/30',
  'Travel': 'bg-indigo-900/40 text-indigo-200 border-indigo-700/30',
  'Other': 'bg-gray-800/40 text-gray-200 border-gray-700/30',
}

// Category icons
const CATEGORY_ICONS = {
  'Food & Dining': 'restaurant',
  'Shopping': 'shopping_cart',
  'Transport': 'directions_car',
  'Entertainment': 'movie',
  'Groceries': 'local_grocery_store',
  'Bills & Utilities': 'receipt_long',
  'Healthcare': 'medical_services',
  'Travel': 'flight',
  'Other': 'more_horiz',
}

function CategoryBadge({ category }) {
  const style = CATEGORY_STYLES[category] || CATEGORY_STYLES['Other']
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {category || 'Other'}
    </span>
  )
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  useEffect(() => {
    fetch('/api/transactions/?limit=500')
      .then(res => res.json())
      .then(data => {
        setTransactions(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(transactions.map(tx => tx.category).filter(Boolean))
    return ['all', ...Array.from(cats)]
  }, [transactions])

  // Filter transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter(tx => {
      const matchesSearch = searchQuery === '' ||
        tx.merchant.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || tx.category === selectedCategory
      return matchesSearch && matchesCategory
    })
  }, [transactions, searchQuery, selectedCategory])

  // Paginate
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage)
  const paginatedTransactions = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage
    return filteredTransactions.slice(start, start + itemsPerPage)
  }, [filteredTransactions, currentPage])

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchQuery, selectedCategory])

  const formatDate = (dateStr) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

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
      <header className="flex flex-col gap-4">
        <h2 className="text-3xl md:text-4xl font-black text-white tracking-tight">Transactions</h2>
        <p className="text-gray-400">
          {filteredTransactions.length} transactions found
        </p>
      </header>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            type="text"
            placeholder="Search merchants..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-surface-dark border border-border-dark rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {/* Category filter */}
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="appearance-none pl-10 pr-10 py-2.5 bg-surface-dark border border-border-dark rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent cursor-pointer min-w-[180px]"
          >
            {categories.map(cat => (
              <option key={cat} value={cat} className="bg-surface-dark">
                {cat === 'all' ? 'All Categories' : cat}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" size={18} />
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-surface-dark rounded-xl border border-border-dark overflow-hidden">
        {paginatedTransactions.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-400">
            {transactions.length === 0
              ? 'No transactions found. Sync bills from Gmail first.'
              : 'No transactions match your filters.'}
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-800/40 text-gray-400 font-semibold border-b border-border-dark">
                  <tr>
                    <th className="px-6 py-4 w-28">Date</th>
                    <th className="px-6 py-4">Merchant</th>
                    <th className="px-6 py-4 w-40">Category</th>
                    <th className="px-6 py-4 text-right w-32">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-dark">
                  {paginatedTransactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-700/30 transition-colors">
                      <td className="px-6 py-4 text-gray-400 whitespace-nowrap">
                        {formatDate(tx.transaction_date)}
                      </td>
                      <td className="px-6 py-4 text-white font-medium">
                        <span className="line-clamp-1" title={tx.merchant}>{tx.merchant}</span>
                      </td>
                      <td className="px-6 py-4">
                        <CategoryBadge category={tx.category} />
                      </td>
                      <td className={`px-6 py-4 text-right font-medium whitespace-nowrap ${
                        tx.amount < 0 ? 'text-emerald-400' : 'text-white'
                      }`}>
                        {tx.currency || 'TWD'} {Math.abs(tx.amount).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-border-dark bg-gray-800/20">
                <p className="text-sm text-gray-400">
                  Showing {(currentPage - 1) * itemsPerPage + 1} - {Math.min(currentPage * itemsPerPage, filteredTransactions.length)} of {filteredTransactions.length}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="p-2 rounded-lg bg-surface-dark border border-border-dark text-gray-400 hover:text-white hover:bg-hover-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft size={18} />
                  </button>
                  <span className="text-sm text-gray-400 min-w-[80px] text-center">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="p-2 rounded-lg bg-surface-dark border border-border-dark text-gray-400 hover:text-white hover:bg-hover-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronRight size={18} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
