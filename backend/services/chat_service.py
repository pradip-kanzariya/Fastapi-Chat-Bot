from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import json
import os
import logging
from fastapi import HTTPException
import numpy as np
from backend.models.models import ChatHistory
from backend.llm.bedrock_sevice import BedrockServices
from backend.utils import format_created_at

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


def call_llm(messages, max_tokens=2000, temperature=0.7, top_p=0.95, top_k=50):
    """Call AWS Bedrock LLM with given messages and return the generated text."""
    try:
        body = {
            "anthropic_version": os.getenv("AWS_ANTHROPIC_VERSION"),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "system": (
                "You are a helpful assistant. Use recent past chats if useful. "
                "Provide structured explanations, examples, code blocks, and summaries when needed."
            ),
            "messages": messages,
        }

        response = BedrockServices.client.invoke_model(
            modelId=os.getenv("AWS_LLM_ID"),
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def build_messages(retrieved_chats, new_question):
    """Generate message for llm."""
    messages = []
    
    for chat in retrieved_chats:
        if chat.file_data:
            messages.append({"role": "user","content": f"Previously the user uploaded this document:\n\n{chat.file_data}"})
        messages.append({"role": "user", "content": chat.user_question})
        messages.append({"role": "assistant", "content": chat.model_answer})
    
    messages.append({"role": "user", "content": new_question})
    return messages

def retrive_similar_chats(query_embeddings, stored_chats, top_k=3):
    """Retrive similar chats."""
    scored = []
    for chat in stored_chats:
        # Convert from JSON string → list[float] → numpy array
        embedding = json.loads(chat.embedding)
        embedding = np.array(embedding, dtype=np.float32)
        score = cosine_similarity(query_embeddings, embedding)
        scored.append((score, chat))
    scored.sort(key= lambda x: x[0], reverse=True)
    return [chat for _, chat in scored[:top_k]]

def cosine_similarity(a, b):
    """Check similarity of "a" and "b"."""
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
