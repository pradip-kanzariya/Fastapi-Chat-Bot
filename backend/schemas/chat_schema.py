from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile, File

class SendMessage(BaseModel):
    """Schema for route send message."""
    session_id : str
    question : str
    file: Optional[UploadFile] = File(None)

class ChatCreate(BaseModel):
    """Schema for new chat entry."""
    session_id: str
    user_id: str
    question: str
    answer: str
    file_data: Optional[str] = None
    embedding: Optional[str] = None