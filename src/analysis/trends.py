"""Spending trend analysis."""
from datetime import date, timedelta
from typing import Dict, List
from collections import defaultdict

from src.db import get_session, Transaction
from sqlalchemy import extract, func


def get_daily_spending(days: int = 30) -> List[Dict]:
    """Get daily spending for the last N days."""
    with get_session() as session:
        start_date = date.today() - timedelta(days=days)

        results = session.query(
            Transaction.transaction_date,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.transaction_date >= start_date
        ).group_by(Transaction.transaction_date).order_by(
            Transaction.transaction_date
        ).all()

        return [
            {
                "date": str(d),
                "amount": round(total, 2)
            }
            for d, total in results
        ]


def get_monthly_trend(months: int = 12) -> List[Dict]:
    """Get monthly spending trend for the last N months."""
    with get_session() as session:
        today = date.today()
        start_year = today.year if today.month > months else today.year - 1
        start_month = (today.month - months) % 12 or 12

        results = session.query(
            extract('year', Transaction.transaction_date).label('year'),
            extract('month', Transaction.transaction_date).label('month'),
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).group_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).order_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).all()

        return [
            {
                "year": int(year),
                "month": int(month),
                "total_amount": round(total, 2),
                "transaction_count": count
            }
            for year, month, total, count in results
        ]


def calculate_average_spending(months: int = 6) -> Dict:
    """Calculate average monthly spending."""
    trend = get_monthly_trend(months)
    if not trend:
        return {"average": 0, "min": 0, "max": 0}

    amounts = [m["total_amount"] for m in trend]
    return {
        "average": round(sum(amounts) / len(amounts), 2),
        "min": round(min(amounts), 2),
        "max": round(max(amounts), 2),
        "months_analyzed": len(amounts)
    }
