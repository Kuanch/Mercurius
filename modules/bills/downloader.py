import time
import base64
from pathlib import Path
from typing import List, Generator, Dict
from core.services.gmail import GmailService

def iter_parts(part: Dict) -> Generator[Dict, None, None]:
    """Yield all parts in the payload tree."""
    if not part:
        return
    yield part
    for sub in part.get("parts", []):
        yield from iter_parts(sub)

def save_raw_email(service: GmailService, msg_id: str, dest: Path) -> None:
    """Save the full raw message for further S/MIME processing."""
    raw_msg = service.service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    data = base64.urlsafe_b64decode(raw_msg["raw"].encode("UTF-8"))
    dest.write_bytes(data)
    print(f"Saved raw S/MIME message to {dest}")

def download_attachments(service: GmailService, msg_id: str, dest_dir: Path) -> None:
    """Download normal attachments or save raw S/MIME messages."""
    message = service.get_message_full(msg_id)
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

        att = service.get_attachment(msg_id, att_id)
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
        service = GmailService()
        a_month_ago = int(time.time()) - 30 * 24 * 60 * 60
        query = f"subject:信用卡 subject:帳單 has:attachment filename:.pdf larger:200K after:{a_month_ago} "
        
        # Use search_messages from GmailService which returns list of dicts with 'id'
        messages = service.search_messages(query)
        message_ids = [m["id"] for m in messages]
        
        dest = Path("attachments")
        for msg_id in message_ids:
            download_attachments(service, msg_id, dest)
    except Exception as error:
        print(f"An error occurred: {error}")
