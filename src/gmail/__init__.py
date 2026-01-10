"""Gmail integration module."""
from src.gmail.auth import get_gmail_service
from src.gmail.fetcher import fetch_bills

__all__ = ["get_gmail_service", "fetch_bills"]
