import base64
import os
import time
from pathlib import Path
from typing import List, Generator, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service():
    """Authenticate and return the Gmail service object."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def list_recent_messages(service, days: int = 3) -> List[str]:
    """Return message IDs for messages received in the last given days."""
    after_ts = int(time.time()) - days * 24 * 60 * 60
    query = f"after:{after_ts}"
    results = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
    msgs = results.get("messages", [])
    return [m["id"] for m in msgs]


def search_messages(service, query: str) -> List[str]:
    """Return message IDs for a Gmail search query."""
    results = (
        service.users().messages().list(userId="me", q=query, maxResults=100).execute()
    )
    return [m["id"] for m in results.get("messages", [])]


def iter_parts(part: Dict) -> Generator[Dict, None, None]:
    """Yield all parts in the payload tree."""
    if not part:
        return
    yield part
    for sub in part.get("parts", []):
        yield from iter_parts(sub)


def save_raw_email(service, msg_id: str, dest: Path) -> None:
    """Save the full raw message for further S/MIME processing."""
    raw_msg = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    data = base64.urlsafe_b64decode(raw_msg["raw"].encode("UTF-8"))
    dest.write_bytes(data)
    print(f"Saved raw S/MIME message to {dest}")


def download_attachments(service, msg_id: str, dest_dir: Path) -> None:
    """Download normal attachments or save raw S/MIME messages."""
    message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = message.get("payload", {})
    headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
    subject = headers.get("Subject", "(No Subject)")
    print(f"Processing message: {subject} (ID: {msg_id})")

    dest_dir.mkdir(parents=True, exist_ok=True)
    parts = list(iter_parts(payload))

    for part in parts:
        filename = part.get("filename")
        body = part.get("body", {})
        att_id = body.get("attachmentId")

        if not filename or not att_id:
            continue
        if not filename.endswith(".pdf"):
            print(f"Skipping non-PDF attachment: {filename}")
            continue

        att = service.users().messages().attachments().get(userId="me", messageId=msg_id, id=att_id).execute()
        data = att["data"]

        if data:
            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            out_path = dest_dir / filename
            out_path.write_bytes(file_data)
            print(f"Saved attachment: {out_path}")
        else:
            print(f"Download failed for {filename} since the data part is missing, downloading raw mail.")
            raw_dir = dest_dir / "smime_raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            save_raw_email(service, msg_id, raw_dir / f"{msg_id}.eml")


def download_bills():
    try:
        service = get_service()
        a_month_ago = int(time.time()) - 30 * 24 * 60 * 60
        query = f"subject:信用卡 subject:帳單 has:attachment filename:.pdf larger:200K after:{a_month_ago} "
        message_ids = search_messages(service, query)
        dest = Path("attachments")
        for msg_id in message_ids:
            download_attachments(service, msg_id, dest)
    except HttpError as error:
        print(f"An error occurred: {error}")
