from pydantic import BaseModel
from fastapi import Form
from typing import Optional

class SendMessage(BaseModel):
    """Schema for route send message."""
    session_id : str = Form(...)
    question : str = Form(...)

class ChatCreate(BaseModel):
    """Schema for new chat entry."""
    session_id: str
    user_id: str
    question: str
    answer: str
    file_data: Optional[str] = None
    embedding: Optional[str] = None