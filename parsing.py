import os
import json
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

def parsing():
    """Main function to parse and decrypt PDFs."""
    raise NotImplementedError("This function is not yet implemented.")

def parse_pdf():
    """Entry point for parsing PDFs."""
    uncrypt_pdf()
    parsing()
