import { useState, useEffect } from 'react'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/transactions/?limit=100')
      .then(res => res.json())
      .then(data => {
        setTransactions(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Transactions</h2>

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Merchant</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {transactions.map(tx => (
              <tr key={tx.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-900">{tx.transaction_date}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{tx.merchant}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{tx.category || '-'}</td>
                <td className={`px-6 py-4 text-sm text-right font-medium ${tx.amount < 0 ? 'text-green-600' : 'text-gray-900'}`}>
                  TWD {tx.amount.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {transactions.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No transactions found. Sync bills from Gmail first.
          </div>
        )}
      </div>
    </div>
  )
}
