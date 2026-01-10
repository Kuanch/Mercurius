"""Sinopac Bank (永豐銀行) statement parser."""
from src.parsers.base import GenericParser


class SinopacParser(GenericParser):
    """Parser for Sinopac Bank credit card statements."""

    bank_name = "sinopac"
    password_key = "SINO"
