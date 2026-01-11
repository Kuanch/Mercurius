import { useState, useEffect, useMemo } from 'react'
import { Wallet, TrendingUp, RefreshCw, ChevronDown, ChevronUp, CreditCard, Download, ArrowUpDown } from 'lucide-react'

// Bank logo mapping - you can replace with actual logos
const BANK_LOGOS = {
  'ESUN': '/logos/esun.png',
  'FUBON': '/logos/fubon.png',
  'SINOPAC': '/logos/sinopac.png',
  'TSB': '/logos/tsb.png',
  'CBCC': '/logos/cbcc.png',
}

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

function CategoryBadge({ category }) {
  const style = CATEGORY_STYLES[category] || CATEGORY_STYLES['Other']
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {category || 'Other'}
    </span>
  )
}

function SortIcon({ field, sortField, sortOrder }) {
  if (sortField !== field) {
    return <ArrowUpDown size={14} className="text-gray-600" />
  }
  return sortOrder === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
}

function BillCard({ bill, onToggle, isOpen }) {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(false)
  const [sortField, setSortField] = useState('date')
  const [sortOrder, setSortOrder] = useState('desc')

  useEffect(() => {
    if (isOpen && transactions.length === 0) {
      setLoading(true)
      fetch(`/api/bills/${bill.id}`)
        .then(res => res.json())
        .then(data => {
          setTransactions(data.transactions || [])
          setLoading(false)
        })
        .catch(() => setLoading(false))
    }
  }, [isOpen, bill.id, transactions.length])

  const sortedTransactions = useMemo(() => {
    return [...transactions].sort((a, b) => {
      let aVal, bVal
      if (sortField === 'date') {
        aVal = new Date(a.date).getTime()
        bVal = new Date(b.date).getTime()
      } else if (sortField === 'merchant') {
        aVal = a.merchant.toLowerCase()
        bVal = b.merchant.toLowerCase()
      } else if (sortField === 'amount') {
        aVal = a.amount
        bVal = b.amount
      }
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
      return 0
    })
  }, [transactions, sortField, sortOrder])

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const formatDate = (dateStr) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div className="bg-surface-dark rounded-xl border border-border-dark overflow-hidden animate-fade-in">
      {/* Summary header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-4 px-6 py-5 hover:bg-hover-dark transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="bg-white/90 p-2 rounded-lg border border-border-dark h-12 w-12 flex items-center justify-center shrink-0">
            <CreditCard className="text-gray-700" size={24} />
          </div>
          <div className="text-left">
            <p className="text-white font-bold">{bill.bank}</p>
            <p className="text-gray-400 text-sm">
              {new Date(bill.statement_date).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right hidden sm:block">
            <p className="text-white font-bold">TWD {bill.total_amount?.toLocaleString() || 0}</p>
            <p className="text-gray-400 text-xs">{bill.transaction_count} transactions</p>
          </div>
          <ChevronDown
            className={`text-gray-500 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
            size={20}
          />
        </div>
      </button>

      {/* Expanded transactions */}
      {isOpen && (
        <div className="border-t border-border-dark">
          {loading ? (
            <div className="px-6 py-8 text-center text-gray-400">Loading transactions...</div>
          ) : transactions.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-400">No transactions found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-800/40 text-gray-400 font-semibold border-b border-border-dark">
                  <tr>
                    <th className="px-6 py-4 w-24 cursor-pointer select-none" onClick={() => handleSort('date')}>
                      <span className="flex items-center gap-1 hover:text-white transition-colors">
                        Date <SortIcon field="date" sortField={sortField} sortOrder={sortOrder} />
                      </span>
                    </th>
                    <th className="px-6 py-4 cursor-pointer select-none" onClick={() => handleSort('merchant')}>
                      <span className="flex items-center gap-1 hover:text-white transition-colors">
                        Merchant <SortIcon field="merchant" sortField={sortField} sortOrder={sortOrder} />
                      </span>
                    </th>
                    <th className="px-6 py-4 text-right cursor-pointer select-none" onClick={() => handleSort('amount')}>
                      <span className="flex items-center gap-1 justify-end hover:text-white transition-colors">
                        Amount <SortIcon field="amount" sortField={sortField} sortOrder={sortOrder} />
                      </span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-dark">
                  {sortedTransactions.slice(0, 10).map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-700/30 transition-colors">
                      <td className="px-6 py-4 text-gray-400">{formatDate(tx.date)}</td>
                      <td className="px-6 py-4 text-white font-medium">
                        <span className="line-clamp-1">{tx.merchant}</span>
                      </td>
                      <td className="px-6 py-4 text-right text-white font-medium">
                        TWD {tx.amount.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {transactions.length > 10 && (
            <div className="p-4 bg-gray-800/20 border-t border-border-dark flex justify-end">
              <button className="text-primary hover:text-primary/80 text-sm font-bold flex items-center gap-1 transition-colors">
                View All {transactions.length} Transactions
                <ChevronDown className="rotate-[-90deg]" size={16} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [bills, setBills] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [expandedBillId, setExpandedBillId] = useState(null)
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  })

  useEffect(() => {
    const [year, month] = selectedMonth.split('-')
    Promise.all([
      fetch(`/api/analysis/monthly?year=${year}&month=${month}`).then(r => r.json()),
      fetch('/api/bills/').then(r => r.json())
    ])
      .then(([summaryData, billsData]) => {
        setSummary(summaryData)
        // Filter bills by selected month
        const filtered = billsData.filter(b => {
          const d = new Date(b.statement_date)
          return d.getFullYear() === parseInt(year) && d.getMonth() + 1 === parseInt(month)
        })
        setBills(filtered)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [selectedMonth])

  const handleSync = async () => {
    setSyncing(true)
    try {
      const [year, month] = selectedMonth.split('-')
      const res = await fetch(`/api/bills/sync?year=${year}&month=${month}`, { method: 'POST' })
      const data = await res.json()
      if (!res.ok) {
        alert(data.detail || 'Sync failed')
      } else {
        alert(`Synced ${data.bills_processed} bills, ${data.transactions_imported} transactions for ${year}-${month}`)
        // Refresh data without changing page
        const [summaryRes, billsRes] = await Promise.all([
          fetch(`/api/analysis/monthly?year=${year}&month=${month}`).then(r => r.json()),
          fetch('/api/bills/').then(r => r.json())
        ])
        setSummary(summaryRes)
        const filtered = billsRes.filter(b => {
          const d = new Date(b.statement_date)
          return d.getFullYear() === parseInt(year) && d.getMonth() + 1 === parseInt(month)
        })
        setBills(filtered)
      }
    } catch (e) {
      alert('Sync failed: Could not connect to server')
    }
    setSyncing(false)
  }

  // Generate month options (last 12 months)
  const monthOptions = Array.from({ length: 12 }, (_, i) => {
    const d = new Date()
    d.setMonth(d.getMonth() - i)
    return {
      value: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      label: d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    }
  })

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
          <h2 className="text-3xl md:text-4xl font-black text-white tracking-tight">Bill Overview</h2>
          <div className="relative w-fit">
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="appearance-none bg-transparent text-gray-400 text-base md:text-lg font-medium pr-8 pl-0 border-0 focus:ring-0 cursor-pointer focus:outline-none"
            >
              {monthOptions.map(opt => (
                <option key={opt.value} value={opt.value} className="bg-surface-dark">
                  {opt.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500" size={18} />
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex h-10 items-center justify-center rounded-lg px-4 bg-surface-dark border border-border-dark text-gray-200 text-sm font-bold hover:bg-hover-dark transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`mr-2 ${syncing ? 'animate-spin' : ''}`} size={18} />
            {syncing ? 'Syncing...' : 'Sync Gmail'}
          </button>
          <button className="hidden sm:flex h-10 items-center justify-center rounded-lg px-4 bg-surface-dark border border-border-dark text-gray-200 text-sm font-bold hover:bg-hover-dark transition-colors">
            <Download className="mr-2" size={18} />
            Export
          </button>
        </div>
      </header>

      {/* Total Balance Card */}
      <section className="grid grid-cols-1 gap-4">
        <div className="flex flex-col gap-1 rounded-xl p-6 bg-surface-dark border border-border-dark">
          <div className="flex justify-between items-start">
            <p className="text-gray-400 text-sm font-semibold uppercase tracking-wider">Total Spending</p>
            <span className="text-primary bg-primary/10 p-1.5 rounded-lg">
              <Wallet size={20} />
            </span>
          </div>
          <p className="text-white text-3xl font-bold tracking-tight mt-2">
            TWD {summary?.total_amount?.toLocaleString() || 0}
          </p>
          <div className="flex items-center gap-1 mt-1">
            <TrendingUp className="text-emerald-500" size={14} />
            <p className="text-emerald-400 text-xs font-bold">
              {summary?.transaction_count || 0} transactions
            </p>
          </div>
        </div>
      </section>

      {/* Card Statements */}
      <section className="flex flex-col gap-6">
        <h3 className="text-xl font-bold text-white">Card Statements</h3>

        {bills.length === 0 ? (
          <div className="bg-surface-dark rounded-xl border border-border-dark p-8 text-center">
            <p className="text-gray-400 mb-4">No bills found for this period.</p>
            <button
              onClick={handleSync}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium"
            >
              Sync Bills from Gmail
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {bills.map((bill) => (
              <BillCard
                key={bill.id}
                bill={bill}
                isOpen={expandedBillId === bill.id}
                onToggle={() => setExpandedBillId(expandedBillId === bill.id ? null : bill.id)}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
