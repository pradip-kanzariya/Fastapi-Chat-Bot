from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import Annotated
from backend.services.llm_services import call_llm
from backend.dependencies.dependencies import get_db
from backend.llm.bedrock_sevice import BedrockServices
from backend.schemas.chat_schema import SendMessage
from backend.auth.auth import decode_jwt_token
from backend.services.file_processor import process_uploaded_file
from backend.services.chat_service import build_messages, retrive_similar_chats
from backend.api.crud.chat_crud import save_chat_entry, fetch_chat_sessions, fetch_session_messages, fetch_user_chats

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send_message")
async def send_message_and_generate_answer(
    chat_data: Annotated[SendMessage, Form()],
    db: Session = Depends(get_db),
    current_user: dict = Depends(decode_jwt_token)
):
    """Send user question (and optional file) to LLM and return answer."""
    try:

        # Fetch previous chats
        all_chats = fetch_user_chats(db=db, session_id=chat_data.session_id, user_id=current_user["user_id"])

        # Handle file (if uploaded)
        file_data, combined_question = await process_uploaded_file(chat_data.file, chat_data.question)

        # Generate embeddings
        query_embeddings = BedrockServices.generate_embeddings(text=combined_question)
        similar_chat = retrive_similar_chats(query_embeddings, all_chats)
        messages = build_messages(similar_chat, combined_question)

        # Call LLM
        result = call_llm(messages)

        # Save chat in DB
        chat_entry = save_chat_entry(
            db=db,
            session_id=chat_data.session_id,
            user_id=current_user["user_id"],
            question=chat_data.question,
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
