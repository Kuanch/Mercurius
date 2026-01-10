"""FastAPI application for Mercurius web interface."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.db import init_db, seed_categories
from src.api.routes import bills, transactions, analysis, chat

# Initialize database on startup
init_db()
seed_categories()

app = FastAPI(
    title="Mercurius API",
    description="Credit Card Bill Analyzer API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bills.router, prefix="/api/bills", tags=["Bills"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Serve static files (React build) in production
web_dist = Path(__file__).parent.parent.parent / "web" / "dist"
if web_dist.exists():
    app.mount("/", StaticFiles(directory=str(web_dist), html=True), name="static")
