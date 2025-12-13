import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from core.config import GMAIL_TOKEN_PATH, GMAIL_CREDS_PATH, GMAIL_SCOPES

def get_gmail_credentials() -> Credentials:
    """Authenticate and return the Gmail service credentials."""
    creds = None
    if os.path.exists(GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, GMAIL_SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(GMAIL_CREDS_PATH):
                raise FileNotFoundError(f"Credentials file not found at {GMAIL_CREDS_PATH}")
                
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDS_PATH, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(GMAIL_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
            
    return creds
