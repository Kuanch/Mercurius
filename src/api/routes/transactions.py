"""Transactions API routes."""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from src.db import TransactionRepository

router = APIRouter()


class TransactionResponse(BaseModel):
    id: int
    transaction_date: date
    merchant: str
    amount: float
    currency: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get transactions with pagination."""
    transactions = TransactionRepository.get_all(limit=limit, offset=offset)
    return [
        TransactionResponse(
            id=tx.id,
            transaction_date=tx.transaction_date,
            merchant=tx.merchant,
            amount=tx.amount,
            currency=tx.currency,
            category=tx.category.name if tx.category else None
        )
        for tx in transactions
    ]


@router.get("/range")
def get_transactions_by_range(
    start: date = Query(...),
    end: date = Query(...)
):
    """Get transactions within a date range."""
    transactions = TransactionRepository.get_by_date_range(start, end)
    return [
        {
            "id": tx.id,
            "date": tx.transaction_date,
            "merchant": tx.merchant,
            "amount": tx.amount,
            "category": tx.category.name if tx.category else None
        }
        for tx in transactions
    ]
