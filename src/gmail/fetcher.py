"""Gmail bill fetcher - download credit card statements."""
import base64
import time
from pathlib import Path
from typing import List, Dict, Generator, Optional

from googleapiclient.errors import HttpError

from src.config import ATTACHMENTS_DIR, GMAIL_SEARCH_DAYS, GMAIL_SEARCH_QUERY
from src.gmail.auth import get_gmail_service


def search_messages(service, query: str, max_results: int = 100) -> List[str]:
    """Return message IDs matching the Gmail search query."""
    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    return [m["id"] for m in results.get("messages", [])]


def iter_parts(part: Dict) -> Generator[Dict, None, None]:
    """Yield all parts in the MIME payload tree."""
    if not part:
        return
    yield part
    for sub in part.get("parts", []):
        yield from iter_parts(sub)


def save_raw_email(service, msg_id: str, dest: Path) -> None:
    """Save raw S/MIME email for further processing."""
    raw_msg = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    data = base64.urlsafe_b64decode(raw_msg["raw"].encode("UTF-8"))
    dest.write_bytes(data)
    print(f"Saved raw S/MIME message to {dest}")


def download_attachments(service, msg_id: str, dest_dir: Path) -> List[Path]:
    """Download PDF attachments from a message."""
    message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = message.get("payload", {})
    headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
    subject = headers.get("Subject", "(No Subject)")
    print(f"Processing: {subject}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []

    for part in iter_parts(payload):
        filename = part.get("filename")
        body = part.get("body", {})
        att_id = body.get("attachmentId")

        if not filename or not att_id:
            continue
        if not filename.lower().endswith(".pdf"):
            continue

        att = service.users().messages().attachments().get(
            userId="me", messageId=msg_id, id=att_id
        ).execute()
        data = att.get("data")

        if data:
            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            out_path = dest_dir / filename
            out_path.write_bytes(file_data)
            print(f"  Downloaded: {filename}")
            downloaded.append(out_path)
        else:
            print(f"  Failed to download {filename}, saving raw email...")
            raw_dir = dest_dir / "smime_raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            save_raw_email(service, msg_id, raw_dir / f"{msg_id}.eml")

    return downloaded


def fetch_bills(days: int = None, year: int = None, month: int = None) -> List[Path]:
    """
    Fetch credit card bills from Gmail.

    Args:
        days: Number of days to search back (default from config, ignored if year/month specified)
        year: Specific year to fetch (e.g., 2025)
        month: Specific month to fetch (1-12)

    Returns:
        List of paths to downloaded PDF files
    """
    import calendar
    from datetime import datetime

    try:
        service = get_gmail_service()

        if year and month:
            # Fetch specific month
            start_date = datetime(year, month, 1)
            _, last_day = calendar.monthrange(year, month)
            end_date = datetime(year, month, last_day, 23, 59, 59)
            after_ts = int(start_date.timestamp())
            before_ts = int(end_date.timestamp())
            query = f"{GMAIL_SEARCH_QUERY} after:{after_ts} before:{before_ts}"
            print(f"Searching Gmail for bills from {year}-{month:02d}...")
        else:
            # Fetch last N days
            if days is None:
                days = GMAIL_SEARCH_DAYS
            after_ts = int(time.time()) - days * 24 * 60 * 60
            query = f"{GMAIL_SEARCH_QUERY} after:{after_ts}"
            print(f"Searching Gmail for bills from last {days} days...")

        message_ids = search_messages(service, query)
        print(f"Found {len(message_ids)} messages with potential bills")

        all_downloaded = []
        for msg_id in message_ids:
            downloaded = download_attachments(service, msg_id, ATTACHMENTS_DIR)
            all_downloaded.extend(downloaded)

        print(f"\nDownloaded {len(all_downloaded)} PDF files")
        return all_downloaded

    except HttpError as error:
        print(f"Gmail API error: {error}")
        return []
