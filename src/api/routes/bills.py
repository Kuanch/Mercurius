"""Bills API routes."""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from src.db import BillRepository, TransactionRepository, CategoryRepository
from src.gmail import fetch_bills
from src.parsers import parse_pdf

router = APIRouter()


class BillResponse(BaseModel):
    id: int
    bank: str
    statement_date: date
    total_amount: Optional[float]
    transaction_count: int

    class Config:
        from_attributes = True


class SyncResponse(BaseModel):
    message: str
    bills_processed: int
    transactions_imported: int


@router.get("/", response_model=List[BillResponse])
def list_bills():
    """Get all bills."""
    bills = BillRepository.get_all()
    result = []
    for bill in bills:
        # Calculate total from transactions if not set
        total = bill.total_amount
        if total is None and bill.transactions:
            total = sum(tx.amount for tx in bill.transactions if tx.amount > 0)
        result.append(BillResponse(
            id=bill.id,
            bank=bill.bank,
            statement_date=bill.statement_date,
            total_amount=total,
            transaction_count=len(bill.transactions) if bill.transactions else 0
        ))
    return result


@router.get("/{bill_id}")
def get_bill(bill_id: int):
    """Get a specific bill with transactions."""
    bill = BillRepository.get_by_id(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {
        "id": bill.id,
        "bank": bill.bank,
        "statement_date": bill.statement_date,
        "total_amount": bill.total_amount,
        "transactions": [
            {
                "id": tx.id,
                "date": tx.transaction_date,
                "merchant": tx.merchant,
                "amount": tx.amount
            }
            for tx in bill.transactions
        ]
    }


def sync_bills_task(days: int = None, year: int = None, month: int = None):
    """Background task to sync bills."""
    pdf_files = fetch_bills(days=days, year=year, month=month)
    bills_processed = 0
    transactions_imported = 0

    for pdf_path in pdf_files:
        try:
            result = parse_pdf(pdf_path)
            bank = result["bank"]
            stmt_date = result["statement_date"] or date.today()

            if BillRepository.exists(bank, stmt_date):
                continue

            bill = BillRepository.create(
                bank=bank,
                statement_date=stmt_date,
                pdf_path=str(pdf_path)
            )

            for tx in result["transactions"]:
                tx["category_id"] = CategoryRepository.auto_categorize(tx["merchant"])

            TransactionRepository.bulk_create(result["transactions"], bill.id)
            bills_processed += 1
            transactions_imported += len(result["transactions"])

        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    return bills_processed, transactions_imported


@router.post("/sync", response_model=SyncResponse)
def sync_bills(
    days: int = Query(None, description="Days to look back (ignored if year/month provided)"),
    year: int = Query(None, description="Specific year to sync"),
    month: int = Query(None, ge=1, le=12, description="Specific month to sync (1-12)")
):
    """Sync bills from Gmail for a specific month or last N days."""
    try:
        bills_processed, transactions_imported = sync_bills_task(days=days, year=year, month=month)
        return SyncResponse(
            message="Sync completed",
            bills_processed=bills_processed,
            transactions_imported=transactions_imported
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "invalid_grant" in error_msg or "refresh" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Gmail authentication expired. Please run 'python -m cli sync' in terminal to re-authenticate."
            )
        raise HTTPException(status_code=500, detail=f"Sync failed: {error_msg}")
