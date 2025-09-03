from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging

from backend.dependencies.dependencies import get_db
from backend.models.models import ChatHistory
from backend.llm.bedrock_sevice import BedrockServices
from backend.auth.auth import decode_jwt_token
from backend.services.file_processor import process_uploaded_file
from backend.services.chat_service import save_chat_entry, fetch_chat_sessions, fetch_session_messages, call_llm, build_messages, retrive_similar_chats

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send_message")
async def send_message_and_generate_answer(
    session_id: str = Form(...),
    question: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(decode_jwt_token)
):
    """Send user question (and optional file) to LLM and return answer."""
    try:
        # Fetch previous chats
        all_chats = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id,
            ChatHistory.user_id == current_user["user_id"]
        ).all()

        # Handle file (if uploaded)
        file_data, combined_question = await process_uploaded_file(file, question)

        # Generate embeddings
        query_embeddings = BedrockServices.generate_embeddings(text=combined_question)
        similar_chat = retrive_similar_chats(query_embeddings, all_chats)
        messages = build_messages(similar_chat, combined_question)

        # Call LLM
        result = call_llm(messages)

        # Save chat in DB
        chat_entry = save_chat_entry(
            db=db,
            session_id=session_id,
            user_id=current_user["user_id"],
            question=question,
            answer=result,
            file_data=file_data,
            embedding=query_embeddings
        )

        return {"user": current_user, "message": result}

    except Exception as e:
        logger.error(f"send_message_and_generate_answer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat_sessions")
async def get_user_chat_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(decode_jwt_token)
):
    """Get all chat history of current user."""
    try:
        sessions_list = fetch_chat_sessions(db, current_user["user_id"])
        return {"current_user": current_user, "sessions_list": sessions_list}
    except Exception as e:
        logger.error(f"get_user_chat_history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/")
async def get_user_chat_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(decode_jwt_token)
):
    """Get all messages of a specific session for the current user."""
    try:
        chats_list = fetch_session_messages(db, session_id, current_user["user_id"])
        return {"current_user": current_user, "all_messages": chats_list}
    except Exception as e:
        logger.error(f"get_user_chat_session_messages failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
