"""Configuration management for Mercurius."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
DB_PATH = DATA_DIR / "mercurius.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
ATTACHMENTS_DIR.mkdir(exist_ok=True)

# Gmail OAuth
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# PDF passwords for different banks
PDF_PASSWORDS = {
    "CBG": os.getenv("PDF_PASSWORD_CBG", ""),
    "ESUN": os.getenv("PDF_PASSWORD_ESUN", ""),
    "TSB": os.getenv("PDF_PASSWORD_TSB", ""),
    "SINO": os.getenv("PDF_PASSWORD_SINO", ""),
    "FUBON": os.getenv("PDF_PASSWORD_FUBON", ""),
}

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Gmail search defaults
GMAIL_SEARCH_DAYS = int(os.getenv("GMAIL_SEARCH_DAYS", "30"))
GMAIL_SEARCH_QUERY = 'subject:信用卡 subject:帳單 has:attachment filename:.pdf larger:200K'

# Database
DATABASE_URL = f"sqlite:///{DB_PATH}"
