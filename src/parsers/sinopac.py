"""Sinopac Bank (永豐銀行) statement parser."""
import re
from src.parsers.base import GenericParser


class SinopacParser(GenericParser):
    """Parser for Sinopac Bank credit card statements."""

    bank_name = "sinopac"
    password_key = "SINO"

    def preprocess_text(self, text: str) -> str:
        """Join wrapped transaction lines for Sinopac format.

        Sinopac has foreign transactions split like:
        '12/07 12/09 8809 FOREIGN MERCHANT NAME SAN'
        'FRANCISCOUS 627 12/06 USD20.000'

        This joins them into single lines.
        """
        lines = text.split('\n')
        result = []
        i = 0

        # Pattern for lines starting with date
        date_start = re.compile(r'^\d{2}/\d{2}\s+\d{2}/\d{2}')
        # Pattern for continuation lines (starts with text, has amount and USD)
        continuation = re.compile(r'^[A-Z]+\s+(\d[\d,]*)\s+\d{2}/\d{2}\s+USD')

        while i < len(lines):
            line = lines[i]

            # Check if this line starts with a date but might be incomplete
            if date_start.match(line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                match = continuation.match(next_line)
                if match:
                    # Extract the TWD amount from continuation line
                    twd_amount = match.group(1)
                    # Join lines, adding the TWD amount to the first line
                    joined = line.rstrip() + ' ' + twd_amount
                    result.append(joined)
                    i += 2
                    continue

            result.append(line)
            i += 1

        return '\n'.join(result)
