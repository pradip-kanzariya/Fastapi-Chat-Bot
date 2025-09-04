from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import json
import logging
from fastapi import HTTPException
import numpy as np
from backend.models.models import ChatHistory
from backend.utils.helper import format_created_at

logger = logging.getLogger(__name__)


def save_chat_entry(db: Session, session_id: str, user_id: str, question: str, answer: str, file_data: str, embedding):
    """Save a new chat entry in DB."""
    try:
        chat_entry = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            user_question=question,
            model_answer=answer,
            file_data=file_data,
            embedding=json.dumps(embedding)
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)
        return chat_entry
    except Exception as e:
        logger.error(f"Store chat in db failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def fetch_chat_sessions(db: Session, user_id: str):
    """Fetch all chat sessions for a user."""
    try:
        sessions = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.created_at))
            .all()
        )
        all_sessions = []
        for chat in sessions:
            all_sessions.append({
                "id": chat.id,
                "session_id": chat.session_id,
                "created_at": format_created_at(chat.created_at)
            })
        return all_sessions
    except Exception as e:
        logger.error(f"Fetch chat sessions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def fetch_session_messages(db: Session, session_id: str, user_id: str):
    """Fetch messages for a specific session."""
    try:
        session_chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id, ChatHistory.user_id == user_id)
            .order_by(asc(ChatHistory.created_at))
            .all()
        )
        all_messages = []
        for chat in session_chats:
            all_messages.append({
                "id": chat.id,
                "session_id": chat.session_id,
                "question": chat.user_question,
                "answer": chat.model_answer,
                "created_at": format_created_at(chat.created_at),
            })
        return all_messages
    except Exception as e:
        logger.error(f"Fetch session messages failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def fetch_user_chats(db: Session, session_id: str, user_id: str):
    """Fetch user's previous chats"""
    try:
        all_chats = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id,
            ChatHistory.user_id == user_id
        ).all()
        return all_chats
    except Exception as e:
        logger.error(f"Fetch user's chats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))