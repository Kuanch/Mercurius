"""Analysis API routes."""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import date

from src.analysis import (
    get_monthly_summary,
    get_yearly_summary,
    get_spending_by_category,
    get_top_merchants,
    get_monthly_trend,
    calculate_average_spending
)

router = APIRouter()


@router.get("/monthly")
def monthly_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Get monthly spending summary."""
    today = date.today()
    year = year or today.year
    month = month or today.month
    return get_monthly_summary(year, month)


@router.get("/yearly")
def yearly_summary(year: Optional[int] = Query(None)):
    """Get yearly spending summary by month."""
    year = year or date.today().year
    return get_yearly_summary(year)


@router.get("/categories")
def spending_by_category(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Get spending breakdown by category."""
    return get_spending_by_category(year, month)


@router.get("/merchants")
def top_merchants(
    limit: int = Query(10, ge=1, le=50),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Get top merchants by spending."""
    return get_top_merchants(limit, year, month)


@router.get("/trends")
def spending_trends(months: int = Query(12, ge=1, le=36)):
    """Get monthly spending trends."""
    return get_monthly_trend(months)


@router.get("/average")
def average_spending(months: int = Query(6, ge=1, le=24)):
    """Get average monthly spending."""
    return calculate_average_spending(months)
