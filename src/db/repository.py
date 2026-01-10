"""Database repository for CRUD operations."""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from src.db.models import Bill, Transaction, Category, MerchantCategory, get_session


class BillRepository:
    """Repository for Bill operations."""

    @staticmethod
    def create(bank: str, statement_date: date, pdf_path: str = None,
               due_date: date = None, total_amount: float = None) -> Bill:
        with get_session() as session:
            bill = Bill(
                bank=bank,
                statement_date=statement_date,
                pdf_path=pdf_path,
                due_date=due_date,
                total_amount=total_amount
            )
            session.add(bill)
            session.commit()
            session.refresh(bill)
            return bill

    @staticmethod
    def get_by_id(bill_id: int) -> Optional[Bill]:
        with get_session() as session:
            return session.query(Bill).filter_by(id=bill_id).first()

    @staticmethod
    def get_all() -> List[Bill]:
        with get_session() as session:
            return session.query(Bill).order_by(Bill.statement_date.desc()).all()

    @staticmethod
    def exists(bank: str, statement_date: date) -> bool:
        with get_session() as session:
            return session.query(Bill).filter_by(
                bank=bank, statement_date=statement_date
            ).first() is not None


class TransactionRepository:
    """Repository for Transaction operations."""

    @staticmethod
    def create(transaction_date: date, merchant: str, amount: float,
               bill_id: int = None, post_date: date = None,
               currency: str = "TWD", category_id: int = None,
               raw_description: str = None) -> Transaction:
        with get_session() as session:
            tx = Transaction(
                bill_id=bill_id,
                transaction_date=transaction_date,
                post_date=post_date,
                merchant=merchant,
                amount=amount,
                currency=currency,
                category_id=category_id,
                raw_description=raw_description
            )
            session.add(tx)
            session.commit()
            session.refresh(tx)
            return tx

    @staticmethod
    def bulk_create(transactions: List[dict], bill_id: int = None) -> List[Transaction]:
        with get_session() as session:
            created = []
            for tx_data in transactions:
                tx = Transaction(
                    bill_id=bill_id,
                    transaction_date=tx_data["transaction_date"],
                    post_date=tx_data.get("post_date"),
                    merchant=tx_data["merchant"],
                    amount=tx_data["amount"],
                    currency=tx_data.get("currency", "TWD"),
                    category_id=tx_data.get("category_id"),
                    raw_description=tx_data.get("raw_description")
                )
                session.add(tx)
                created.append(tx)
            session.commit()
            return created

    @staticmethod
    def get_all(limit: int = None, offset: int = 0) -> List[Transaction]:
        with get_session() as session:
            query = session.query(Transaction).order_by(Transaction.transaction_date.desc())
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()

    @staticmethod
    def get_by_date_range(start: date, end: date) -> List[Transaction]:
        with get_session() as session:
            return session.query(Transaction).filter(
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end
            ).order_by(Transaction.transaction_date.desc()).all()

    @staticmethod
    def get_monthly_summary(year: int, month: int) -> dict:
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
                "total_amount": total,
                "transaction_count": count,
                "transactions": transactions
            }


class CategoryRepository:
    """Repository for Category operations."""

    @staticmethod
    def get_all() -> List[Category]:
        with get_session() as session:
            return session.query(Category).all()

    @staticmethod
    def get_by_name(name: str) -> Optional[Category]:
        with get_session() as session:
            return session.query(Category).filter_by(name=name).first()

    @staticmethod
    def auto_categorize(merchant: str) -> Optional[int]:
        """Auto-categorize based on merchant name keywords."""
        with get_session() as session:
            # First check learned mappings
            mapping = session.query(MerchantCategory).filter_by(merchant=merchant).first()
            if mapping:
                return mapping.category_id

            # Then check keyword matches
            categories = session.query(Category).all()
            merchant_lower = merchant.lower()
            for cat in categories:
                if cat.keywords:
                    for keyword in cat.keywords:
                        if keyword.lower() in merchant_lower:
                            return cat.id

            # Default to "Other"
            other = session.query(Category).filter_by(name="Other").first()
            return other.id if other else None

    @staticmethod
    def learn_category(merchant: str, category_id: int):
        """Learn a merchant → category mapping."""
        with get_session() as session:
            existing = session.query(MerchantCategory).filter_by(merchant=merchant).first()
            if existing:
                existing.category_id = category_id
            else:
                mapping = MerchantCategory(merchant=merchant, category_id=category_id)
                session.add(mapping)
            session.commit()
