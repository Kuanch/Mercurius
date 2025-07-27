import os
import json
import re
from pypdf import PdfReader, PdfWriter


def uncrypt(src_path: str, dst_path: str, password: str) -> None:
    """Decrypt a PDF file with the given password."""
    reader = PdfReader(src_path)
    if not reader.is_encrypted:
        return False
    if not reader.decrypt(password):  # raises if wrong
        return False
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(dst_path, "wb") as f:
        writer.write(f)
    print(f"Saved decrypted copy to {dst_path}")

    return True


def uncrypt_pdf():
    if not os.path.exists("unlocked"):
        os.makedirs("unlocked")
    for filename in os.listdir("attachments"):
        if filename.endswith(".pdf"):
            print(f"Decrypting {filename}...")
            src_path = os.path.join("attachments", filename)
            dst_path = os.path.join("unlocked", filename)

            with open("password.json", "r") as f:
                passwords = json.load(f)
            if filename.startswith("CBG"):
                password = passwords["CBG"]
            elif filename.startswith("ESUM"):
                password = passwords["ESUM"]
            elif filename.startswith("TSB"):
                password = passwords["TSB"]
            elif filename.startswith("永豐"):
                password = passwords["SINO"]

            if uncrypt(src_path, dst_path, password):
                print(f"Successfully decrypted {filename}.")
            else:
                print(f"Failed to decrypt {filename}.")

def _parse_single_pdf(pdf_path: str) -> dict:
    """Extract transaction data from a single PDF file."""
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text.append(t)
    content = "\n".join(text)

    line_re = re.compile(
        r"(?P<consume>\d{2}/\d{2})\s+"  # consume date
        r"(?P<post>\d{2}/\d{2})\s+"      # post date
        r"(?:(?P<card>\d{4})\s+)?"        # optional card last4
        r"(?P<desc>.+?)\s+"               # description
        r"(?P<amount>-?\d[\d,]*)$"       # amount
    )
    total_re = re.compile(r"本期應繳金額合計\s+([\d,]+)")

    transactions = []
    total = None
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        m = line_re.search(line)
        if m:
            data = m.groupdict()
            transactions.append(data)
            continue
        m_total = total_re.search(line)
        if m_total:
            total = m_total.group(1)

    return {"transactions": transactions, "total_due": total}


def parsing():
    """Parse all decrypted PDFs under the 'unlocked' directory."""
    results = {}
    if not os.path.isdir("unlocked"):
        print("No decrypted PDFs found. Run uncrypt_pdf() first.")
        return results

    for filename in os.listdir("unlocked"):
        if not filename.endswith(".pdf"):
            continue
        path = os.path.join("unlocked", filename)
        print(f"Parsing {filename}...")
        results[filename] = _parse_single_pdf(path)

    with open("parsed.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Saved parsed data to parsed.json")
    return results

def parse_pdf():
    """Entry point for parsing PDFs."""
    uncrypt_pdf()
    parsing()
