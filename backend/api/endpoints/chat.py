from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from PyPDF2 import PdfReader
from PIL import Image
from io import BytesIO
import json
import os
import logging
from typing import Optional
import pytesseract
from backend.dependencies.dependencies import get_db
from backend.models.models import ChatHistory
from backend.utils import retrive_similar_chats, format_created_at, build_messages
from backend.llm.bedrock import Bedrock
from backend.auth.auth import decode_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def message(
    session_id: str, 
    question: str, 
    file: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db),
    current_user: str = Depends(decode_jwt_token)
    ):
    try:
        all_chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .filter(ChatHistory.user_id == current_user["user_id"])
            .all()
        )
        file_data = None
        combined_question = question

        if file:
            content = await file.read()
            file_name = file.filename
            file_type = file.content_type
            file_size = len(content)
            logger.info(f"file_name = {file_name}, file_type = {file_type}, file_size = {file_size}")

            try:
                if file.filename.lower().endswith(".pdf"):
                    pdf_stream = BytesIO(content)
                    reader = PdfReader(pdf_stream)
                    pdf_text = "".join([page.extract_text() or "" for page in reader.pages])
                    file_data = pdf_text.strip()
                    combined_question = f"The user uploaded the following PDF:\n\n{file_data}\n\nUser's question: {question}"

                elif file.content_type.startswith("image/"):
                    image = Image.open(BytesIO(content))
                    file_data = pytesseract.image_to_string(image)
                    combined_question = f"The user uploaded the following Image:\n\n{file_data}\n\nUser's question: {question}"

                else:
                    file_data = content.decode("utf-8").strip()
                    combined_question = f"The user uploaded the following document:\n\n{file_data}\n\nUser's question: {question}"

            except Exception as e:
                file_data = f"[Could not extract text: {e}]"
                combined_question = f"User's question: {question}"

        query_embeddings = Bedrock.generate_embeddings(combined_question)
        similar_chat = retrive_similar_chats(query_embeddings, all_chats)
        messages = build_messages(similar_chat, combined_question)

        body = json.dumps({
            "anthropic_version": os.getenv("AWS_ANTHROPIC_VERSION"),
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 50,
            "system": (
                "You are a helpful assistant. Use recent past chats if useful. "
                "Provide structured explanations, examples, code blocks, and summaries when needed."
            ),
            "messages": messages
        })

        response = Bedrock.client.invoke_model(
            modelId=os.getenv("AWS_LLM_ID"),
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())["content"][0]["text"]

        chat_entry = ChatHistory(
            session_id=session_id,
            user_id=current_user["user_id"],
            user_question=question,
            model_answer=result,
            file_data=file_data,
            embedding=json.dumps(query_embeddings)
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)

        return JSONResponse({"user":current_user, "message": result}, status_code=200)

    except Exception as e:
        logger.error(e)


@router.get("/")
async def get_chat_history(db: Session = Depends(get_db), current_user: str = Depends(decode_jwt_token)):
    try:
        all_chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == current_user["user_id"])
            .order_by(desc(ChatHistory.created_at)).all()
        )
        chats_list = [
            {
                "id": chat.id,
                "session_id": chat.session_id,
                "question": chat.user_question,
                "answer": chat.model_answer,
                "created_at": format_created_at(chat.created_at),
                "file_data": chat.file_data,
                "embedding": chat.embedding
            }
            for chat in all_chats
        ]
        return JSONResponse({"current_user":current_user, "all_chats": chats_list}, status_code=200)
    except Exception as e:
        logger.error(e)


@router.get("/{session_id}/")
async def get_chat_by_session(session_id: str, db: Session = Depends(get_db), current_user: str = Depends(decode_jwt_token)):
    try:
        chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .filter(ChatHistory.user_id == current_user["user_id"])
            .order_by(asc(ChatHistory.created_at)).all()
        )
        chats_list = [
            {
                "id": chat.id,
                "session_id": chat.session_id,
                "question": chat.user_question,
                "answer": chat.model_answer,
                "created_at": format_created_at(chat.created_at),
            }
            for chat in chats
        ]
        return JSONResponse({"current_user":current_user, "all_chats": chats_list}, status_code=200)
    except Exception as e:
        logger.error(e)
