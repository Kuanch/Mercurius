"""Cathay United Bank (國泰世華) statement parser."""
from src.parsers.base import GenericParser


class CathayParser(GenericParser):
    """Parser for Cathay United Bank credit card statements."""

    bank_name = "cathay"
    password_key = "CATHAY"
