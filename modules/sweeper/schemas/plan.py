from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

class GmailQuery(BaseModel):
    q: str = Field(..., description="Gmail search query, e.g. 'newer_than:7d subject:(receipt OR invoice) has:attachment' \n只允許 Gmail 官方語法")
    max_results: int = Field(100, ge=1, le=500)

class Limits(BaseModel):
    max_threads: int = Field(200, ge=1, le=2000)
    allow_labels: List[str] = Field(default_factory=lambda: ["Newsletters", "Receipts", "Sandbox/Drafts"])
    allow_folders: List[str] = Field(default_factory=list)
    max_drafts: int = Field(50, ge=0, le=200)

class ActLabel(BaseModel):
    type: Literal["label"]
    name: str

class ActArchive(BaseModel):
    type: Literal["archive"]

class ActMoveTo(BaseModel):
    type: Literal["move_to"]
    folder: str

class ActMarkRead(BaseModel):
    type: Literal["mark_read"]

class ActStar(BaseModel):
    type: Literal["star"]

class ActUnstar(BaseModel):
    type: Literal["unstar"]

class ActDraftReply(BaseModel):
    type: Literal["draft_reply"]
    template_id: Literal["unsubscribe_zh", "unsubscribe_en", "ack_receipt"]

Action = Union[ActLabel, ActArchive, ActMoveTo, ActMarkRead, ActStar, ActUnstar, ActDraftReply]

class SmartFilter(BaseModel):
    topic: Optional[Literal["Work", "Finance", "Promotion", "Social", "Updates", "Forum", "Spam"]] = None
    urgency: Optional[Literal["High", "Medium", "Low"]] = None

class Plan(BaseModel):
    goal: str
    queries: List[GmailQuery]
    actions: List[Action]
    smart_filters: Optional[SmartFilter] = None
    dry_run: bool = True
    confirm: bool = False
    limits: Limits = Field(default_factory=Limits)
