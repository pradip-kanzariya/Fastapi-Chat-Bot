from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile, File

class SendMessage(BaseModel):
    """Schema for route send_message_and_generate_answer."""
    session_id : str
    question : str
    file: Optional[UploadFile] = File(None)
