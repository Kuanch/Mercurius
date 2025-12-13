import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Gmail Configuration
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN", str(BASE_DIR / "token.json"))
GMAIL_CREDS_PATH = os.getenv("GMAIL_CREDS", str(BASE_DIR / "credentials.json"))
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]

# OpenAI Configuration
OPENAI_API_KEY_PATH = os.getenv("OPENAI_KEY_FILE", str(BASE_DIR / "chat_key.txt"))

def get_openai_key() -> str:
    if os.path.exists(OPENAI_API_KEY_PATH):
        with open(OPENAI_API_KEY_PATH, "r") as f:
            return f.read().strip()
    return os.getenv("OPENAI_API_KEY", "")
