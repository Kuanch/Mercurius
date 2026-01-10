"""TSB Bank statement parser."""
from src.parsers.base import GenericParser


class TsbParser(GenericParser):
    """Parser for TSB credit card statements."""

    bank_name = "tsb"
    password_key = "TSB"
