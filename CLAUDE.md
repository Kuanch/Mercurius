# Mercurius - Credit Card Bill Analyzer

## Quick Start

```bash
# Install dependencies
pip install -e .

# Initialize database
python -m cli init

# Sync bills from Gmail
python -m cli sync

# View spending summary
python -m cli summary

# Chat with AI about spending
python -m cli chat

# Start web server
python -m cli serve
```

## Project Structure

```
src/
├── config.py          # Configuration from .env
├── gmail/             # Gmail OAuth & bill fetching
├── parsers/           # PDF parsing (bank-specific)
├── db/                # SQLAlchemy models & repository
├── analysis/          # Spending analysis
├── ai/                # OpenAI chat integration
└── api/               # FastAPI backend
web/src/               # React frontend
cli.py                 # CLI entry point
```

## Configuration

Copy `.env.example` to `.env` and fill in:
- `PDF_PASSWORD_*` - PDF decryption passwords for each bank
- `OPENAI_API_KEY` - For AI chat feature

## Supported Banks (Taiwan)

- E.SUN Bank (玉山銀行)
- Fubon Bank (富邦銀行)
- Sinopac Bank (永豐銀行)
- TSB
- CBCC/CBG (中國信託)

## API Endpoints

- `GET /api/analysis/monthly` - Monthly summary
- `GET /api/transactions/` - List transactions
- `GET /api/analysis/categories` - Spending by category
- `POST /api/chat/` - AI chat
- `POST /api/bills/sync` - Sync from Gmail

## Notes for Development

- Gmail OAuth tokens in `token.json` (gitignored)
- Database at `data/mercurius.db`
- PDFs downloaded to `data/attachments/`
- Frontend dev: `cd web && npm run dev`
- Backend dev: `python -m cli serve`

## Refactoring Complete (2025-01)

Migrated from flat script structure to modular architecture:
- Old: `download.py`, `parsing.py`, `main.py`
- New: `src/` module with proper separation of concerns
- Added SQLite database instead of text files
- Added FastAPI REST API
- Added React frontend with Tailwind CSS
- Added AI chat for spending analysis
