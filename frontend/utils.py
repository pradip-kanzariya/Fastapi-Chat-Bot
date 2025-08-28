import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------- Backend Setup -------------------
backend_host = os.getenv("BACKEND_HOST", "localhost")
backend_port = os.getenv("BACKEND_PORT", "8000")
backend_url = f"http://{backend_host}:{backend_port}"

def fetch_all_sessions():
    """Get all sessions from backend (only ones with chats)."""
    try:
        res = requests.get(f"{backend_url}/get_chat/")
        all_chats = res.json().get("all_chats", [])

        # Sort all chats by created_at (descending: newest first)
        all_chats_sorted = sorted(all_chats, key=lambda x: x["created_at"], reverse=True)
        # Extract unique session_ids in order
        session_ids = []
        for chat in all_chats_sorted:
            if chat["session_id"] not in session_ids:
                session_ids.append(chat["session_id"])
        return session_ids
    except Exception as e:
        return f"Error : {e}"
    

def fetch_session_chats(session_id):
    """Fetch all chats for a specific session."""
    try:
        res = requests.get(f"{backend_url}/get_chat/{session_id}/")
        if res.status_code == 200:
            return res.json().get("all_chats", [])
    except Exception as e:
        return f"Error : {e}"

def send_message(session_id, question, file_data=None):
    """Send a chat message to the backend."""
    try:
        data = {
            "session_id": session_id,
            "question": question
        }

        res = requests.post(
            f"{backend_url}/chat/",
            params=data,   # form fields
            files=file_data   # file upload (if provided)
        )

        if res.status_code == 200:
            return res.json().get("message", "")
        else:
            return res.json()

    except Exception as e:
        return f"Error : {e}"