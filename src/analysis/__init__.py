"""Analysis module for spending insights."""
from src.analysis.summary import get_monthly_summary, get_yearly_summary, get_spending_by_bank
from src.analysis.categories import get_spending_by_category, get_top_merchants
from src.analysis.trends import get_daily_spending, get_monthly_trend, calculate_average_spending

__all__ = [
    "get_monthly_summary",
    "get_yearly_summary",
    "get_spending_by_bank",
    "get_spending_by_category",
    "get_top_merchants",
    "get_daily_spending",
    "get_monthly_trend",
    "calculate_average_spending",
]
