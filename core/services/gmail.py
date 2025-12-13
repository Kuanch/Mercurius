from __future__ import annotations
import base64
from typing import Dict, List, Optional, Generator
from email.message import EmailMessage
from googleapiclient.discovery import build
from core.auth.google import get_gmail_credentials

class GmailService:
    def __init__(self):
        self.creds = get_gmail_credentials()
        self.service = build("gmail", "v1", credentials=self.creds)

    def search_messages(self, q: str, max_results: int = 100) -> List[Dict]:
        """Search for messages and return brief metadata."""
        svc = self.service.users().messages()
        messages = []
        page_token = None
        while True:
            resp = svc.list(userId="me", q=q, maxResults=max_results, pageToken=page_token).execute()
            ids = resp.get("messages", [])
            if not ids:
                break
            for it in ids:
                full = self.service.users().messages().get(userId="me", id=it["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"]).execute()
                messages.append({
                    "id": full["id"],
                    "threadId": full.get("threadId"),
                    "snippet": full.get("snippet"),
                    "headers": {h["name"].lower(): h["value"] for h in full.get("payload", {}).get("headers", [])}
                })
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return messages

    def get_message_full(self, msg_id: str) -> Dict:
        """Get full message content."""
        return self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    def get_attachment(self, msg_id: str, att_id: str) -> Dict:
        """Get attachment data."""
        return self.service.users().messages().attachments().get(userId="me", messageId=msg_id, id=att_id).execute()

    def _ensure_label(self, name: str) -> str:
        svc = self.service.users().labels()
        labels = svc.list(userId="me").execute().get("labels", [])
        for lb in labels:
            if lb["name"].lower() == name.lower():
                return lb["id"]
        body = {"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        created = svc.create(userId="me", body=body).execute()
        return created["id"]

    def batch_label(self, ids: List[str], add: Optional[List[str]] = None, remove: Optional[List[str]] = None):
        add = add or []
        remove = remove or []
        add_ids = [self._ensure_label(n) for n in add]
        remove_ids = [] # TODO: Handle remove by name if needed
        body = {"ids": ids, "addLabelIds": add_ids, "removeLabelIds": remove_ids}
        return self.service.users().messages().batchModify(userId="me", body=body).execute()

    def batch_archive(self, ids: List[str]):
        return self.service.users().messages().batchModify(userId="me", body={"ids": ids, "removeLabelIds": ["INBOX"]}).execute()

    def batch_mark_read(self, ids: List[str]):
        return self.service.users().messages().batchModify(userId="me", body={"ids": ids, "removeLabelIds": ["UNREAD"]}).execute()

    def batch_star(self, ids: List[str]):
        return self.service.users().messages().batchModify(userId="me", body={"ids": ids, "addLabelIds": ["STARRED"]}).execute()

    def batch_unstar(self, ids: List[str]):
        return self.service.users().messages().batchModify(userId="me", body={"ids": ids, "removeLabelIds": ["STARRED"]}).execute()

    def create_draft_reply(self, message_id: str, thread_id: str, to_addr: str, subject: str, body_text: str) -> str:
        msg = EmailMessage()
        msg["To"] = to_addr
        msg["Subject"] = "Re: " + subject
        msg.set_content(body_text)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        draft_body = {"message": {"raw": raw, "threadId": thread_id}}
        draft = self.service.users().drafts().create(userId="me", body=draft_body).execute()
        return draft.get("id")
