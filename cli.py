#!/usr/bin/env python3
"""Mercurius CLI - Credit Card Bill Analyzer."""
import click
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def main():
    """Mercurius - Credit Card Bill Analyzer

    Download bills from Gmail, parse them, and analyze your spending.
    """
    pass


@main.command()
def init():
    """Initialize database and seed categories."""
    from src.db import init_db, seed_categories
    console.print("[yellow]Initializing database...[/yellow]")
    init_db()
    seed_categories()
    console.print("[green]Database initialized successfully![/green]")


@main.command()
@click.option("--days", default=30, help="Number of days to search back")
def sync(days):
    """Fetch new bills from Gmail and import to database."""
    from src.gmail import fetch_bills
    from src.parsers import parse_pdf
    from src.db import BillRepository, TransactionRepository, CategoryRepository, init_db

    init_db()

    console.print(f"[yellow]Fetching bills from last {days} days...[/yellow]")
    pdf_files = fetch_bills(days)

    if not pdf_files:
        console.print("[red]No new bills found.[/red]")
        return

    console.print(f"\n[yellow]Parsing {len(pdf_files)} PDFs...[/yellow]")
    for pdf_path in pdf_files:
        try:
            result = parse_pdf(pdf_path)
            bank = result["bank"]
            stmt_date = result["statement_date"] or date.today()

            # Check if already imported
            if BillRepository.exists(bank, stmt_date):
                console.print(f"  [dim]{pdf_path.name} - already imported[/dim]")
                continue

            # Create bill record
            bill = BillRepository.create(
                bank=bank,
                statement_date=stmt_date,
                pdf_path=str(pdf_path)
            )

            # Import transactions with auto-categorization
            for tx in result["transactions"]:
                tx["category_id"] = CategoryRepository.auto_categorize(tx["merchant"])

            TransactionRepository.bulk_create(result["transactions"], bill.id)
            console.print(f"  [green]{pdf_path.name} - imported {len(result['transactions'])} transactions[/green]")

        except Exception as e:
            console.print(f"  [red]{pdf_path.name} - error: {e}[/red]")

    console.print("\n[green]Sync complete![/green]")


@main.command()
@click.option("--limit", default=50, help="Number of transactions to show")
def list(limit):
    """List recent transactions."""
    from src.db import TransactionRepository, init_db
    init_db()

    transactions = TransactionRepository.get_all(limit=limit)

    if not transactions:
        console.print("[yellow]No transactions found. Run 'mercurius sync' first.[/yellow]")
        return

    table = Table(title="Recent Transactions")
    table.add_column("Date", style="cyan")
    table.add_column("Merchant", style="white")
    table.add_column("Amount", justify="right", style="green")

    for tx in transactions:
        amount_str = f"TWD {tx.amount:,.0f}"
        if tx.amount < 0:
            amount_str = f"[red]{amount_str}[/red]"
        table.add_row(str(tx.transaction_date), tx.merchant[:40], amount_str)

    console.print(table)


@main.command()
@click.option("--year", default=None, type=int, help="Year (default: current)")
@click.option("--month", default=None, type=int, help="Month (default: current)")
def summary(year, month):
    """Show monthly spending summary."""
    from src.analysis import get_monthly_summary, get_spending_by_category
    from src.db import init_db
    init_db()

    today = date.today()
    year = year or today.year
    month = month or today.month

    data = get_monthly_summary(year, month)
    categories = get_spending_by_category(year, month)

    # Build summary text
    summary_lines = [
        f"[bold]Gross Spending:[/bold] TWD {data.get('gross_spending', data['total_amount']):,.0f}",
    ]
    if data.get('credits', 0) != 0:
        summary_lines.append(f"[bold]Cashback/Refunds:[/bold] TWD {data['credits']:,.0f}")
    summary_lines.extend([
        f"[bold]Net Spending:[/bold] TWD {data['total_amount']:,.0f}",
        f"[bold]Transactions:[/bold] {data['transaction_count']}",
    ])

    panel = Panel(
        "\n".join(summary_lines),
        title=f"Spending Summary - {year}/{month:02d}",
        border_style="green"
    )
    console.print(panel)

    if categories:
        table = Table(title="By Category")
        table.add_column("Category")
        table.add_column("Amount", justify="right")
        table.add_column("Count", justify="right")

        for cat in sorted(categories, key=lambda x: x['total_amount'], reverse=True):
            if cat['total_amount'] > 0:
                table.add_row(
                    cat['category'],
                    f"TWD {cat['total_amount']:,.0f}",
                    str(cat['transaction_count'])
                )

        console.print(table)


@main.command()
def chat():
    """Interactive AI chat about your spending."""
    from src.ai import chat as ai_chat
    from src.db import init_db
    init_db()

    console.print(Panel(
        "Ask me anything about your spending!\nType 'quit' to exit.",
        title="Mercurius AI Chat",
        border_style="blue"
    ))

    history = []
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            response = ai_chat(user_input, history)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

            console.print(f"[bold green]AI:[/bold green] {response}\n")

        except KeyboardInterrupt:
            break

    console.print("[yellow]Goodbye![/yellow]")


@main.command()
def serve():
    """Start the web API server."""
    import uvicorn
    console.print("[yellow]Starting API server on http://localhost:8000[/yellow]")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
