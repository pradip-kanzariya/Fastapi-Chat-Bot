from fastapi import FastAPI, Depends, File, UploadFile
from PyPDF2 import PdfReader
from io import BytesIO
from PIL import Image
import pytesseract
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import json
import os
from typing import Optional
from dotenv import load_dotenv
from backend.llm import Bedrock
from backend.db import Base, engine, get_db
from backend.models import ChatHistory
from backend.embeddings import generate_embeddings
from backend.utils import retrive_similar_chats, format_created_at, build_messages

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_DIR")

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

fastapi_app = FastAPI()

@fastapi_app.get("/")
async def helth_check():
    return JSONResponse(
        {"message": "Success"},
        status_code=200
    )

@fastapi_app.post("/chat/")
async def message(session_id: str, question: str, file: Optional[UploadFile] = File(None), db: Session = Depends(get_db)):
    try:
        all_chats = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
        file_data = None
        combined_question = question
        if file:
            content = await file.read()
            file_name = file.filename
            file_type = file.content_type
            file_size = len(content)
            print(f"file_name = {file_name}")
            print(f"file_type = {file_type}")
            print(f"file_size = {file_size}")
            try:
                if file.filename.lower().endswith(".pdf"):
                    pdf_stream = BytesIO(content)
                    reader = PdfReader(pdf_stream)
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                    
                    file_data = pdf_text.strip()
                    combined_question = (
                        f"The user uploaded the following PDF document:\n\n"
                        f"{file_data}\n\n"
                        f"User's question: {question}"
                    )
                elif file.content_type.startswith("image/"):
                    image = Image.open(BytesIO(content))
                    file_data = pytesseract.image_to_string(image)
                    combined_question = (
                        f"The user uploaded the following Image document:\n\n"
                        f"{file_data}\n\n"
                        f"User's question: {question}"
                    )
                else:
                    # Try normal UTF-8 text file
                    file_data = content.decode("utf-8").strip()
                    combined_question = (
                        f"The user uploaded the following document:\n\n"
                        f"{file_data}\n\n"
                        f"User's question: {question}"
                    )
            except Exception as e:
                file_data = f"[Could not extract text: {e}]"
                combined_question = f"User's question: {question}"

        query_embeddings = generate_embeddings(combined_question)
        similar_chat = retrive_similar_chats(query_embeddings, all_chats)
        messages = build_messages(similar_chat, combined_question)

        # Prepare body for LLM
        body = json.dumps({
            "anthropic_version": os.getenv("AWS_ANTHROPIC_VERSION"),
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 50,
            "system": (
                "You are a helpful assistant. Use latest recent past chats if useful. "
                "Always provide complete answers, structured explanations, and examples if useful. "
                "If a question asks for code, return well-formatted and complete code blocks. "
                "If a question asks for mathematics, highlight result values with explaination. "
                "Use tables, summaries, or bullet points when they improve clarity."
            ),
            "messages": messages
        })

        response = Bedrock.client.invoke_model(
            modelId=os.getenv("AWS_LLM_ID"),
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        result = result["content"][0]["text"]

        chat_entry = ChatHistory(
            session_id=session_id,
            user_question=question,
            model_answer=result,
            file_data=file_data,
            embedding=json.dumps(query_embeddings)
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)

        return JSONResponse({"message": result}, status_code=200)

    except Exception as e:
        error_msg = str(e)
        return JSONResponse({"Error": error_msg}, status_code=500)

@fastapi_app.get("/get_chat/")
async def get_chat_history(db: Session = Depends(get_db)):
    try:
        all_chats = db.query(ChatHistory).order_by(desc(ChatHistory.created_at)).all()
        chats_list = []
        for chat in all_chats:
            chats_list.append({
                "id": chat.id,
                "session_id": chat.session_id,
                "question": chat.user_question,
                "answer": chat.model_answer,
                "created_at": format_created_at(chat.created_at),
                "file_data": chat.file_data,
                "embedding": chat.embedding
            })
        return JSONResponse({"all_chats": chats_list}, status_code=200)
    except Exception as e:
        return JSONResponse({"Error": str(e)}, status_code=500)

@fastapi_app.get("/get_chat/{session_id}/")
async def get_chat_by_session(session_id: str, db: Session = Depends(get_db)):
    try:
        chats_list = []
        chats = (
            db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(asc(ChatHistory.created_at)).all()
        )
        if not chats:
            return JSONResponse({"all_chats": []}, status_code=200)
        for chat in chats:
            chats_list.append({
                    "id": chat.id,
                    "session_id": chat.session_id,
                    "question": chat.user_question,
                    "answer": chat.model_answer,
                    "created_at": format_created_at(chat.created_at),
                })
        return JSONResponse({"all_chats": chats_list}, status_code=200)
    except Exception as e:
        return JSONResponse({"Error": str(e)}, status_code=500)
