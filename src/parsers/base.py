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
    # Matches: MM/DD MM/DD description amount
    # Or: YYY/MM/DD YYY/MM/DD description amount (ROC calendar)
    TRANSACTION_PATTERN = re.compile(r"""
        ^
        (?P<consume>(?:\d{2,3}/)?\d{2}/\d{2})      # Transaction date: 07/07 or 114/06/27
        \s+
        (?P<post>(?:\d{2,3}/)?\d{2}/\d{2})         # Post date
        \s+
        (?P<desc>.+?)                              # Description (non-greedy)
        \s+
        (?P<amount>[-−－]?\d[\d,]*(?:\.\d+)?)      # Amount with optional negative
        \s*$
    """, re.UNICODE | re.VERBOSE | re.MULTILINE)

    def parse_date(self, date_str: str) -> date:
        """Parse date string to date object."""
        parts = date_str.split("/")
        if len(parts) == 3:
            # ROC calendar: YYY/MM/DD
            year = int(parts[0]) + 1911
            month = int(parts[1])
            day = int(parts[2])
        else:
            # MM/DD format - assume current year
            from datetime import datetime
            current_year = datetime.now().year
            month = int(parts[0])
            day = int(parts[1])
            year = current_year
        return date(year, month, day)

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        # Remove commas and normalize minus signs
        cleaned = amount_str.replace(",", "").replace("−", "-").replace("－", "-")
        return float(cleaned)

    def parse(self) -> List[Dict]:
        if not self.text:
            self.decrypt_if_needed()

        transactions = []
        for match in self.TRANSACTION_PATTERN.finditer(self.text):
            try:
                tx = {
                    "transaction_date": self.parse_date(match.group("consume")),
                    "post_date": self.parse_date(match.group("post")),
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
        """Try to extract statement date from filename or content."""
        filename = self.pdf_path.stem

        # Try YYYYMM format first (e.g., 202507)
        date_match = re.search(r'(\d{4})(\d{2})', filename)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                return date(year, month, 1)

        # Try ROC year format YYYMM (e.g., 11406 = 2025/06)
        date_match = re.search(r'(\d{3})(\d{2})', filename)
        if date_match:
            year = int(date_match.group(1)) + 1911
            month = int(date_match.group(2))
            if 1 <= month <= 12:
                return date(year, month, 1)

        return None
