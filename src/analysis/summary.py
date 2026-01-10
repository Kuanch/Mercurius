"""Monthly spending summary analysis."""
from datetime import date
from typing import Dict, List
from collections import defaultdict

from src.db import get_session, Transaction, Category
from sqlalchemy import extract, func


def get_monthly_summary(year: int, month: int) -> Dict:
    """Get spending summary for bills with statement date in the specified month.

    This groups by billing period (statement date) rather than individual
    transaction dates, which better reflects credit card billing cycles.
    """
    from src.db.models import Bill

    with get_session() as session:
        # Get bills with statement date in the specified month
        bills = session.query(Bill).filter(
            extract('year', Bill.statement_date) == year,
            extract('month', Bill.statement_date) == month
        ).all()

        bill_ids = [b.id for b in bills]

        # Get all transactions for these bills
        transactions = session.query(Transaction).filter(
            Transaction.bill_id.in_(bill_ids)
        ).all() if bill_ids else []

        # Calculate gross spending (positive amounts only, excluding payments)
        spending_txs = [tx for tx in transactions if tx.amount > 0]
        gross_spending = sum(tx.amount for tx in spending_txs)

        # Calculate credits/cashback (negative amounts, excluding payment entries)
        credit_txs = [tx for tx in transactions
                      if tx.amount < 0
                      and '自扣' not in tx.merchant
                      and '繳款' not in tx.merchant
                      and '入帳' not in tx.merchant]
        credits = sum(tx.amount for tx in credit_txs)

        # Net spending = gross - cashback/refunds
        net_spending = gross_spending + credits

        return {
            "year": year,
            "month": month,
            "gross_spending": round(gross_spending, 2),
            "credits": round(credits, 2),
            "total_amount": round(net_spending, 2),
            "transaction_count": len(spending_txs),
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
