"""PDF parsers for different bank statements."""
from pathlib import Path
from typing import List, Dict, Optional

from src.parsers.base import BaseParser, GenericParser
from src.parsers.esun import EsunParser
from src.parsers.fubon import FubonParser
from src.parsers.sinopac import SinopacParser
from src.parsers.tsb import TsbParser
from src.parsers.cbcc import CbccParser
from src.parsers.cathay import CathayParser


# Mapping of filename prefixes to parser classes
PARSER_MAP = {
    "ESUN": EsunParser,
    "富邦": FubonParser,
    "永豐": SinopacParser,
    "TSB": TsbParser,
    "CBG": CbccParser,
    "CBGCC": CbccParser,
    "信用卡電子帳單消費明細": CathayParser,
}


def get_parser_for_file(pdf_path: Path) -> BaseParser:
    """Get the appropriate parser for a PDF file based on filename."""
    filename = pdf_path.name
    for prefix, parser_class in PARSER_MAP.items():
        if filename.startswith(prefix):
            return parser_class(pdf_path)
    # Default to generic parser
    return GenericParser(pdf_path)


def parse_pdf(pdf_path: Path) -> Dict:
    """
    Parse a single PDF file.

    Returns:
        Dict with keys: bank, statement_date, transactions
    """
    parser = get_parser_for_file(pdf_path)
    parser.decrypt_if_needed()

    return {
        "bank": parser.get_bank_name(),
        "statement_date": parser.detect_statement_date(),
        "transactions": parser.parse(),
        "pdf_path": str(pdf_path)
    }


def parse_all_pdfs(pdf_dir: Path) -> List[Dict]:
    """Parse all PDFs in a directory."""
    results = []
    for pdf_file in pdf_dir.glob("*.pdf"):
        print(f"Parsing {pdf_file.name}...")
        try:
            result = parse_pdf(pdf_file)
            results.append(result)
            print(f"  Found {len(result['transactions'])} transactions")
        except Exception as e:
            print(f"  Error: {e}")
    return results


__all__ = [
    "BaseParser",
    "GenericParser",
    "EsunParser",
    "FubonParser",
    "SinopacParser",
    "TsbParser",
    "CbccParser",
    "CathayParser",
    "get_parser_for_file",
    "parse_pdf",
    "parse_all_pdfs",
]
