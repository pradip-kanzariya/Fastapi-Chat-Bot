from sqlalchemy import Column, Integer, Text, DateTime, String, ForeignKey
from datetime import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user_question = Column(Text, nullable=True)
    model_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    file_data = Column(Text, nullable=True)
    embedding = Column(Text, nullable=True)

