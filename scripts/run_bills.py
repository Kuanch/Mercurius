import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.bills.downloader import download_bills
from modules.bills.parser import parse_pdf
from modules.bills.chat import run_chat

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_bills.py [download|parse|chat]")
        return

    command = sys.argv[1]
    
    if command == "download":
        download_bills()
    elif command == "parse":
        parse_pdf()
    elif command == "chat":
        run_chat()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: download, parse, chat")

if __name__ == "__main__":
    main()
