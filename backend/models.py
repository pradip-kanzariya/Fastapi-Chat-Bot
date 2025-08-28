from sqlalchemy import Column, Integer, Text, DateTime, String
from datetime import datetime
from backend.db import Base

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_question = Column(Text, nullable=True)
    model_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    file_data = Column(Text, nullable=True)
    embedding = Column(Text, nullable=True)
