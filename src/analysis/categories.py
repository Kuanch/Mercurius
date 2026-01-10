"""Category-based spending analysis."""
from typing import Dict, List
from datetime import date
from collections import defaultdict

from src.db import get_session, Transaction, Category
from sqlalchemy import extract, func


def get_spending_by_category(year: int = None, month: int = None) -> List[Dict]:
    """Get spending breakdown by category."""
    with get_session() as session:
        query = session.query(
            Category.name,
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).outerjoin(Transaction).group_by(Category.id)

        if year:
            query = query.filter(extract('year', Transaction.transaction_date) == year)
        if month:
            query = query.filter(extract('month', Transaction.transaction_date) == month)

        results = query.all()
        return [
            {
                "category": name or "Uncategorized",
                "total_amount": round(total or 0, 2),
                "transaction_count": count or 0
            }
            for name, total, count in results
        ]


def get_top_merchants(limit: int = 10, year: int = None, month: int = None) -> List[Dict]:
    """Get top merchants by spending amount."""
    with get_session() as session:
        query = session.query(
            Transaction.merchant,
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).group_by(Transaction.merchant)

        if year:
            query = query.filter(extract('year', Transaction.transaction_date) == year)
        if month:
            query = query.filter(extract('month', Transaction.transaction_date) == month)

        query = query.order_by(func.sum(Transaction.amount).desc()).limit(limit)
        results = query.all()

        return [
            {
                "merchant": merchant,
                "total_amount": round(total, 2),
                "transaction_count": count
            }
            for merchant, total, count in results
        ]
