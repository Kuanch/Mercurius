"""Fubon Bank (富邦銀行) statement parser."""
from src.parsers.base import GenericParser


class FubonParser(GenericParser):
    """Parser for Fubon Bank credit card statements."""

    bank_name = "fubon"
    password_key = "FUBON"
