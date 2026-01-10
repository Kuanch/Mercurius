"""Base PDF parser for credit card statements."""
import re
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional
from pypdf import PdfReader, PdfWriter

from src.config import PDF_PASSWORDS, DATA_DIR


class BaseParser(ABC):
    """Abstract base class for bank statement parsers."""

    bank_name: str = "unknown"
    password_key: str = None  # Key in PDF_PASSWORDS

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.text = ""

    def decrypt_if_needed(self) -> str:
        """Decrypt PDF if encrypted and return text content."""
        reader = PdfReader(str(self.pdf_path))

        if reader.is_encrypted:
            password = PDF_PASSWORDS.get(self.password_key, "")
            try:
                # Try to access pages without password first
                _ = reader.pages[0]
            except:
                if password:
                    if not reader.decrypt(password):
                        raise ValueError(f"Failed to decrypt {self.pdf_path} with password")
                else:
                    raise ValueError(f"PDF is encrypted but no password configured for {self.password_key}")

        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)

        self.text = "\n".join(text_parts)
        return self.text

    @abstractmethod
    def parse(self) -> List[Dict]:
        """
        Parse transactions from the PDF.

        Returns:
            List of transaction dicts with keys:
            - transaction_date: date
            - post_date: date (optional)
            - merchant: str
            - amount: float
            - currency: str (default TWD)
            - raw_description: str
        """
        pass

    @abstractmethod
    def detect_statement_date(self) -> Optional[date]:
        """Extract the statement date from the PDF."""
        pass

    def get_bank_name(self) -> str:
        return self.bank_name


class GenericParser(BaseParser):
    """
    Generic parser using regex patterns.
    Works for most Taiwan credit card statements.
    """

    bank_name = "generic"

    # Regex pattern for transaction lines
    # Matches various bank formats:
    # - TSB: 114/11/18 114/11/20 description 278  TW
    # - Cathay: 11/16 11/20 description 1,025 8875 TW TWD
    # - ESUN: 11/14 11/17 description TWD 29
    TRANSACTION_PATTERN = re.compile(r"""
        ^
        (?P<consume>(?:\d{2,3}/)?\d{2}/\d{2})      # Transaction date: 07/07 or 114/06/27
        [^\S\n]+                                   # Whitespace (not newline)
        (?P<post>(?:\d{2,3}/)?\d{2}/\d{2})         # Post date
        [^\S\n]+                                   # Whitespace (not newline)
        (?P<desc>[^\n]+?)                          # Description (non-greedy, single line)
        [^\S\n]+                                   # Whitespace (not newline)
        (?P<amount>[-−－]?\d[\d,]*)                # Amount (TWD, integer) - greedy to get first number
        (?:[^\S\n]+\d{4})?                         # Optional card last 4 digits (Cathay)
        (?:[^\S\n]+\d{4})?                         # Optional action card digits (Cathay)
        (?:[^\S\n]+\d{4})?                         # Optional conversion date MMDD (TSB foreign)
        (?:[^\S\n]+[A-Z]{2,3})*                    # Optional country/currency codes
        (?:[^\S\n]+[\d.,]+)?                       # Optional foreign currency amount
        [^\S\n]*$
    """, re.UNICODE | re.VERBOSE | re.MULTILINE)

    def parse_date(self, date_str: str, reference_date: date = None) -> date:
        """Parse date string to date object.

        Args:
            date_str: Date string in MM/DD or YYY/MM/DD (ROC) format
            reference_date: Statement date to infer year for MM/DD format
        """
        parts = date_str.split("/")
        if len(parts) == 3:
            # ROC calendar: YYY/MM/DD
            year = int(parts[0]) + 1911
            month = int(parts[1])
            day = int(parts[2])
        else:
            # MM/DD format - infer year from statement date
            month = int(parts[0])
            day = int(parts[1])

            if reference_date:
                # Transactions are usually from 1-2 months before statement date
                # If transaction month > statement month, it's from previous year
                if month > reference_date.month:
                    year = reference_date.year - 1
                else:
                    year = reference_date.year
            else:
                from datetime import datetime
                year = datetime.now().year

        return date(year, month, day)

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        # Remove commas and normalize minus signs
        cleaned = amount_str.replace(",", "").replace("−", "-").replace("－", "-")
        return float(cleaned)

    def preprocess_text(self, text: str) -> str:
        """Join wrapped transaction lines.

        Some PDFs have transactions split across lines like:
        '114/12/05 114/12/10 中油－大雅路站'
        'TAICHU 600  TW'

        This joins them into single lines for regex matching.
        """
        lines = text.split('\n')
        result = []
        i = 0

        # Pattern for lines starting with date
        date_start = re.compile(r'^\d{2,3}/\d{2}/\d{2}\s+\d{2,3}/\d{2}/\d{2}')
        # Pattern for continuation lines with amount and country code
        # Handles: "TAICHU 278  TW" or "220***93 103  TW"
        continuation = re.compile(r'^\S+\s+\d[\d,]*(?:\.\d+)?\s+[A-Z]{2}\s*$')

        while i < len(lines):
            line = lines[i]
            # Check if this line starts with a date but might be incomplete
            if date_start.match(line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Check if next line looks like a continuation (has amount + country)
                if continuation.match(next_line):
                    # Join the lines
                    result.append(line.rstrip() + ' ' + next_line)
                    i += 2
                    continue
            result.append(line)
            i += 1

        return '\n'.join(result)

    def parse(self) -> List[Dict]:
        if not self.text:
            self.decrypt_if_needed()

        # Preprocess to join wrapped lines
        processed_text = self.preprocess_text(self.text)

        # Get statement date to help infer transaction years
        statement_date = self.detect_statement_date()

        transactions = []
        for match in self.TRANSACTION_PATTERN.finditer(processed_text):
            try:
                tx = {
                    "transaction_date": self.parse_date(match.group("consume"), statement_date),
                    "post_date": self.parse_date(match.group("post"), statement_date),
                    "merchant": match.group("desc").strip(),
                    "amount": self.parse_amount(match.group("amount")),
                    "currency": "TWD",
                    "raw_description": match.group(0).strip()
                }
                transactions.append(tx)
            except (ValueError, IndexError) as e:
                print(f"Warning: Failed to parse line: {match.group(0)} - {e}")
                continue

        return transactions

    def detect_statement_date(self) -> Optional[date]:
        """Try to extract statement date from filename or PDF content."""
        filename = self.pdf_path.stem

        # Try YYYYMM format first (e.g., 202512) - most reliable for this format
        date_match = re.search(r'(\d{4})(\d{2})', filename)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                return date(year, month, 1)

        # For ROC format filenames, prefer PDF content if available
        # (filename often has billing cycle month, not statement date)
        if self.text:
            # Look for "結帳日" followed by YYYY/MM/DD (e.g., "結帳日2025/12/21")
            content_match = re.search(r'結帳日[:\s]*(\d{4})/(\d{2})/(\d{2})', self.text)
            if content_match:
                year = int(content_match.group(1))
                month = int(content_match.group(2))
                day = int(content_match.group(3))
                if 1 <= month <= 12 and 1 <= day <= 31 and 2020 <= year <= 2030:
                    return date(year, month, day)

            # Look for "帳單結帳日" followed by ROC date (e.g., "114/12/14")
            content_match = re.search(r'帳單結帳日[:\s]*(\d{3})/(\d{2})/(\d{2})', self.text)
            if content_match:
                year = int(content_match.group(1)) + 1911
                month = int(content_match.group(2))
                day = int(content_match.group(3))
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return date(year, month, day)

            # Look for standalone ROC date at start of line
            content_match = re.search(r'^(\d{3})/(\d{2})/(\d{2})', self.text, re.MULTILINE)
            if content_match:
                year = int(content_match.group(1)) + 1911
                month = int(content_match.group(2))
                day = int(content_match.group(3))
                # Only use if it looks like a reasonable statement date
                if 1 <= month <= 12 and 1 <= day <= 31 and 2020 <= year <= 2030:
                    return date(year, month, day)

        # Fallback: Try ROC year format YYYMM in filename (e.g., 11411 = 2025/11)
        date_match = re.search(r'(\d{3})(\d{2})(?!\d)', filename)
        if date_match:
            year = int(date_match.group(1)) + 1911
            month = int(date_match.group(2))
            if 1 <= month <= 12:
                return date(year, month, 1)

        return None
