"""Monthly spending summary analysis."""
from datetime import date
from typing import Dict, List
from collections import defaultdict

from src.db import get_session, Transaction, Category
from sqlalchemy import extract, func


def get_monthly_summary(year: int, month: int) -> Dict:
    """Get spending summary for a specific month."""
    with get_session() as session:
        transactions = session.query(Transaction).filter(
            extract('year', Transaction.transaction_date) == year,
            extract('month', Transaction.transaction_date) == month
        ).all()

        total = sum(tx.amount for tx in transactions)
        count = len(transactions)

        return {
            "year": year,
            "month": month,
            "total_amount": round(total, 2),
            "transaction_count": count,
        }


def get_yearly_summary(year: int) -> List[Dict]:
    """Get monthly summaries for an entire year."""
    summaries = []
    for month in range(1, 13):
        summary = get_monthly_summary(year, month)
        if summary["transaction_count"] > 0:
            summaries.append(summary)
    return summaries


def get_spending_by_bank(year: int = None, month: int = None) -> Dict[str, float]:
    """Get total spending grouped by bank."""
    with get_session() as session:
        from src.db.models import Bill
        query = session.query(
            Bill.bank,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).group_by(Bill.bank)

        if year:
            query = query.filter(extract('year', Transaction.transaction_date) == year)
        if month:
            query = query.filter(extract('month', Transaction.transaction_date) == month)

        results = query.all()
        return {bank: round(total, 2) for bank, total in results}
