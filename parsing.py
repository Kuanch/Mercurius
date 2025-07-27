import os
import json
import re
from pypdf import PdfReader, PdfWriter


def uncrypt(src_path: str, dst_path: str, password: str) -> None:
    """Decrypt a PDF file with the given password."""
    reader = PdfReader(src_path)
    if reader.is_encrypted:
        # checking if a password is actually needed to read
        try:
            _ = reader.pages[0]
        except:
            if not reader.decrypt(password):  # raises if wrong
                print(f"Failed to decrypt {src_path} with provided password.")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(dst_path, "wb") as f:
        writer.write(f)
    print(f"Saved decrypted copy to {dst_path}")

def uncrypt_pdf():
    if not os.path.exists("unlocked"):
        os.makedirs("unlocked")
    for filename in os.listdir("attachments"):
        if filename.endswith(".pdf"):
            src_path = os.path.join("attachments", filename)
            dst_path = os.path.join("unlocked", filename)

            with open("password.json", "r") as f:
                passwords = json.load(f)
            if filename.startswith("CBG"):
                password = passwords["CBG"]
            elif filename.startswith("TSB"):
                password = passwords["TSB"]
            elif filename.startswith("永豐"):
                password = passwords["SINO"]
            else:
                password = None
            uncrypt(src_path, dst_path, password)

def parse_single_pdf(pdf_path: str) -> dict:
    """Extract transaction data from a single PDF file."""
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text.append(t)
    content = "\n".join(text)

    pattern = re.compile(r"""
    ^
    (?P<consume>(?:\d{2,3}/)?\d{2}/\d{2})      # 07/07 or 114/06/27
    \s+
    (?P<post>(?:\d{2,3}/)?\d{2}/\d{2})
    \s+
    (?P<desc>.*)                                # everything up to the final number
    \s+
    (?P<amount>[-−－]?\d[\d,]*(?:\.\d+)?)
    (?!.*\d)                                    # ensure this is the LAST numeric token
    .*$                                          # allow trailing letters like "TW"
    """, re.UNICODE | re.VERBOSE)

    transactions = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        m = pattern.search(line)
        if m:
            data = m.groupdict()
            transactions.append(data)
            continue

    return {"transactions": transactions}


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
        results[filename] = parse_single_pdf(path)

    with open("parsed.txt", "w", encoding="utf-8") as f:
        for filename, data in results.items():
            if not data['transactions']:
                continue
            f.write(f"File: {filename}\n")
            for tx in data['transactions']:
                f.write(f"{tx['consume']} {tx['post']} {tx['desc']} {tx['amount']}\n")
            f.write("\n")
    print("Saved parsed data to parsed.json")
    return results

def parse_pdf():
    """Entry point for parsing PDFs."""
    uncrypt_pdf()
    parsing()
