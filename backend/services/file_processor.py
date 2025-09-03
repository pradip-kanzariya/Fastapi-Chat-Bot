from PyPDF2 import PdfReader
from PIL import Image
from io import BytesIO
import pytesseract
import logging

logger = logging.getLogger(__name__)

async def process_uploaded_file(file, user_question: str):
    """Extract text from uploaded file and combine with user question."""
    if not file:
        return None, user_question

    try:
        content = await file.read()
        file_name, file_type = file.filename, file.content_type
        logger.info(f"Uploaded file: {file_name}, Type: {file_type}, Size: {len(content)}")

        if file.filename.lower().endswith(".pdf"):
            pdf_stream = BytesIO(content)
            reader = PdfReader(pdf_stream)
            pdf_text = "".join([page.extract_text() or "" for page in reader.pages])
            file_data = pdf_text.strip()
            combined = f"The user uploaded the following PDF:\n\n{file_data}\n\nUser's question: {user_question}"

        elif file.content_type.startswith("image/"):
            image = Image.open(BytesIO(content))
            file_data = pytesseract.image_to_string(image)
            combined = f"The user uploaded the following Image:\n\n{file_data}\n\nUser's question: {user_question}"

        else:
            file_data = content.decode("utf-8").strip()
            combined = f"The user uploaded the following document:\n\n{file_data}\n\nUser's question: {user_question}"

        return file_data, combined

    except Exception as e:
        logger.error(f"File processing failed: {e}")
        return f"[Could not extract text: {e}]", f"User's question: {user_question}"
