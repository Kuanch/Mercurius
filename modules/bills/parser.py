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
    
    if not os.path.exists("attachments"):
        print("No attachments directory found.")
        return

    for filename in os.listdir("attachments"):
        if filename.endswith(".pdf"):
            src_path = os.path.join("attachments", filename)
            dst_path = os.path.join("unlocked", filename)

            passwords = {}
            if os.path.exists("password.json"):
                with open("password.json", "r") as f:
                    passwords = json.load(f)
            
            if filename.startswith("CBG"):
                password = passwords.get("CBG")
            elif filename.startswith("TSB"):
                password = passwords.get("TSB")
            elif filename.startswith("永豐"):
                password = passwords.get("SINO")
            else:
                password = "F128566230" # Default fallback
            
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

    if not os.path.exists("bill"):
        os.makedirs("bill")

    monthly_bills = {}

    for filename, data in results.items():
        if not data['transactions']:
            print(f"No transactions found in {filename}, skipping.")
            continue
        
        for tx in data['transactions']:
            # Extract month from consume date
            date_str = tx['consume']
            parts = date_str.split('/')
            month = "00"
            if len(parts) == 2:
                month = parts[0]
            elif len(parts) == 3:
                month = parts[1]
            
            month = month.zfill(2)
            
            # Append filename for context
            line = f"{tx['consume']} {tx['desc']} {tx['amount']}"
            
            if month not in monthly_bills:
                monthly_bills[month] = []
            monthly_bills[month].append(line)

    for month, lines in monthly_bills.items():
        out_path = os.path.join("bill", f"bills_{month}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

    print(f"Saved parsed data to bill/ folder (months: {', '.join(monthly_bills.keys())})")
    return results

def parse_pdf():
    """Entry point for parsing PDFs."""
    uncrypt_pdf()
    parsing()
