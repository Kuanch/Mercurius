"""E.SUN Bank (玉山銀行) statement parser."""
from src.parsers.base import GenericParser


class EsunParser(GenericParser):
    """Parser for E.SUN Bank credit card statements."""

    bank_name = "esun"
    password_key = "ESUN"
