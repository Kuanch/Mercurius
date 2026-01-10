"""SQLAlchemy models for Mercurius database."""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import create_engine, ForeignKey, String, Float, Date, DateTime, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

from src.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class Category(Base):
    """Spending categories like Food, Shopping, Transport."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # JSON array of merchant keywords

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")


class Bill(Base):
    """A credit card bill/statement from a bank."""
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    bank: Mapped[str] = mapped_column(String(50), nullable=False)
    statement_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="bill", cascade="all, delete-orphan")

    __table_args__ = (
        # Unique constraint on bank + statement_date
        {"sqlite_autoincrement": True},
    )


class Transaction(Base):
    """Individual credit card transaction."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bills.id"), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    post_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    merchant: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TWD")
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    raw_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bill: Mapped[Optional["Bill"]] = relationship(back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")


class MerchantCategory(Base):
    """Learned mapping from merchant names to categories."""
    __tablename__ = "merchant_categories"

    merchant: Mapped[str] = mapped_column(String(500), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)


# Database engine and session factory
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)


def seed_categories():
    """Seed default categories."""
    default_categories = [
        {"name": "Food & Dining", "keywords": ["餐", "食", "咖啡", "飲", "7-11", "全家", "萊爾富", "OK", "美食", "restaurant", "cafe"]},
        {"name": "Shopping", "keywords": ["購物", "商店", "百貨", "momo", "蝦皮", "PChome", "Amazon", "淘寶"]},
        {"name": "Transport", "keywords": ["交通", "停車", "加油", "uber", "計程車", "高鐵", "台鐵", "捷運"]},
        {"name": "Entertainment", "keywords": ["娛樂", "電影", "遊戲", "Netflix", "Spotify", "YouTube"]},
        {"name": "Bills & Utilities", "keywords": ["水費", "電費", "瓦斯", "電信", "網路", "保險"]},
        {"name": "Healthcare", "keywords": ["醫", "藥", "診所", "醫院", "健康"]},
        {"name": "Travel", "keywords": ["旅", "hotel", "booking", "airbnb", "機票", "航空"]},
        {"name": "Other", "keywords": []},
    ]

    with get_session() as session:
        for cat_data in default_categories:
            existing = session.query(Category).filter_by(name=cat_data["name"]).first()
            if not existing:
                category = Category(name=cat_data["name"], keywords=cat_data["keywords"])
                session.add(category)
        session.commit()
