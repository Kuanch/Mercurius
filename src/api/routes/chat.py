"""Chat API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from src.ai import chat as ai_chat

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat with AI about spending patterns."""
    history = None
    if request.history:
        history = [{"role": m.role, "content": m.content} for m in request.history]

    response = ai_chat(request.message, history)
    return ChatResponse(response=response)
