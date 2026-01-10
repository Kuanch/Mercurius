"""CBCC (中國信託) statement parser."""
from src.parsers.base import GenericParser


class CbccParser(GenericParser):
    """Parser for CBCC credit card statements."""

    bank_name = "cbcc"
    password_key = "CBG"
