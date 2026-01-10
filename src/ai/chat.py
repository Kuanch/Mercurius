"""AI-powered chat for spending analysis using OpenAI."""
from datetime import date
from typing import Optional
from openai import OpenAI

from src.config import OPENAI_API_KEY
from src.analysis import (
    get_monthly_summary,
    get_spending_by_category,
    get_top_merchants,
    get_monthly_trend,
    calculate_average_spending
)
from src.db import TransactionRepository, BillRepository


def build_spending_context() -> str:
    """Build context about user's spending for the AI."""
    from datetime import timedelta

    today = date.today()
    year, month = today.year, today.month

    # Current month summary
    current = get_monthly_summary(year, month)

    # Last month summary
    last_month = month - 1 if month > 1 else 12
    last_year = year if month > 1 else year - 1
    previous = get_monthly_summary(last_year, last_month)

    # Category breakdown
    categories = get_spending_by_category(year, month)

    # Top merchants
    merchants = get_top_merchants(5, year, month)

    # Trends
    averages = calculate_average_spending(6)

    context = f"""User's Credit Card Spending Data:

Current Month ({year}/{month}):
- Gross Spending: TWD {current.get('gross_spending', current['total_amount']):,.0f}
- Cashback/Refunds: TWD {current.get('credits', 0):,.0f}
- Net Spending: TWD {current['total_amount']:,.0f}
- Transactions: {current['transaction_count']}

Last Month ({last_year}/{last_month}):
- Net Spending: TWD {previous['total_amount']:,.0f}
- Transactions: {previous['transaction_count']}

6-Month Average: TWD {averages['average']:,.0f}

Category Breakdown (This Month):
"""
    for cat in categories:
        if cat['total_amount'] > 0:
            context += f"- {cat['category']}: TWD {cat['total_amount']:,.0f} ({cat['transaction_count']} transactions)\n"

    context += "\nTop Merchants (This Month):\n"
    for m in merchants:
        context += f"- {m['merchant']}: TWD {m['total_amount']:,.0f}\n"

    # Add transaction-level details
    context += "\n--- Transaction Details (Recent Bills) ---\n"

    # Get all bills and their transactions
    bills = BillRepository.get_all()
    repo = TransactionRepository()
    all_txs = repo.get_all()

    for bill in sorted(bills, key=lambda b: b.statement_date or date.min, reverse=True)[:4]:
        bill_txs = [t for t in all_txs if t.bill_id == bill.id]
        if not bill_txs:
            continue

        context += f"\n{bill.bank.upper()} (Statement: {bill.statement_date}):\n"

        # Sort by date and amount
        spending_txs = sorted(
            [t for t in bill_txs if t.amount > 0],
            key=lambda t: (-t.amount, t.transaction_date)
        )

        for tx in spending_txs[:15]:  # Top 15 transactions per bill
            context += f"  {tx.transaction_date} | TWD {tx.amount:,.0f} | {tx.merchant[:40]}\n"

        if len(spending_txs) > 15:
            context += f"  ... and {len(spending_txs) - 15} more transactions\n"

        # Show credits/cashback if any
        credit_txs = [t for t in bill_txs if t.amount < 0]
        if credit_txs:
            context += f"  Credits/Cashback:\n"
            for tx in credit_txs[:5]:
                context += f"    {tx.transaction_date} | TWD {tx.amount:,.0f} | {tx.merchant[:35]}\n"

    return context


def chat(user_message: str, conversation_history: list = None) -> str:
    """
    Chat with AI about spending patterns.

    Args:
        user_message: User's question about their spending
        conversation_history: Previous messages in the conversation

    Returns:
        AI's response
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Build system prompt with spending context
    spending_context = build_spending_context()
    system_prompt = f"""You are a helpful financial assistant analyzing credit card spending data.
You have access to the user's spending information and can answer questions about their habits,
provide insights, and suggest ways to manage spending better.

Be concise but helpful. Use the actual numbers from the data.
Respond in the same language the user uses (Chinese or English).

{spending_context}
"""

    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="o3",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with AI: {e}"
