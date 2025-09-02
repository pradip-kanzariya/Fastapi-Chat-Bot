import requests
import jwt
from datetime import datetime, timezone
import logging
from configuration import settings

logger = logging.getLogger(__name__)

backend_host = settings.BACKEND_HOST
backend_port = settings.BACKEND_PORT
backend_url = f"http://{backend_host}:{backend_port}"

def fetch_all_sessions(token):
    """Get all sessions from backend (only ones with chats)."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{backend_url}/chat/", headers=headers)
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
        logger.error(e)
        return []
    

def fetch_session_chats(session_id, token):
    """Fetch all chats for a specific session."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{backend_url}/chat/{session_id}/", headers=headers)
        if res.status_code == 200:
            return res.json().get("all_chats", [])
    except Exception as e:
        logger.error(e)

def send_message(session_id, question, token, file_data=None):
    """Send a chat message to the backend."""
    try:
        data = {
            "session_id": session_id,
            "question": question
        }

        headers = {"Authorization": f"Bearer {token}"}

        res = requests.post(
            f"{backend_url}/chat/",
            headers=headers,
            params=data,   # form fields
            files=file_data,   # file upload (if provided)
        )

        if res.status_code == 200:
            return res.json().get("message", "")

    except Exception as e:
        logger.error(e)
    
def login_user(user_email, user_password):
    try:
        payload = {
            "username": user_email,
            "password": user_password
        }

        res = requests.post(
            f"{backend_url}/user/login",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if res.status_code == 200:
            return res.json()

    except Exception as e:
        logger.error(e)
    
def register_user(username, user_email, user_password):
    try:
        payload = {"username":username, "user_email":user_email, "user_password":user_password}

        res = requests.post(
            f"{backend_url}/user/register",
            json=payload
        )
        if res.status_code == 200:
            return res.json().get("username")
        
    except Exception as e:
        logger.error(e)
    
class TokenData:
    def __init__(self, token: str):
        self.token = token
        try:
            # Decode without verifying signature (since you only need data)
            self.decoded = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            self.decoded = {}

    def is_token_expired(self) -> bool:
        """Check if token is expired"""
        try:
            exp = self.decoded.get("exp")
            if not exp:
                return True
            return datetime.now(timezone.utc).timestamp() > exp
        except Exception:
            return True

    def get_user_info(self) -> dict:
        """Get basic user info from token"""
        try:
            return {
                "username": self.decoded.get("username"),
                "email": self.decoded.get("email"),
                "user_id": self.decoded.get("user_id"),
            }
        except Exception:
            return {}