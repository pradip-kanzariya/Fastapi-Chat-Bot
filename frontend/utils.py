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
        res = requests.get(f"{backend_url}/chat/chat_sessions", headers=headers, timeout=10)

        if res.status_code != 200:
            logger.error(f"fetch_all_sessions failed: {res.status_code} - {res.text}")
            return []

        all_sessions = res.json().get("sessions_list", [])
        all_chats_sorted = sorted(all_sessions, key=lambda x: x["created_at"], reverse=True)

        session_ids = []
        for chat in all_chats_sorted:
            if chat["session_id"] not in session_ids:
                session_ids.append(chat["session_id"])

        return session_ids

    except requests.RequestException as e:
        logger.error(f"Network error while fetching sessions: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in fetch_all_sessions: {e}")
    return []


def fetch_session_chats(session_id, token):
    """Fetch all chats for a specific session."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{backend_url}/chat/session/{session_id}/", headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json().get("all_messages", [])
        else:
            logger.error(f"fetch_session_chats failed: {res.status_code} - {res.text}")

    except requests.RequestException as e:
        logger.error(f"Network error while fetching session chats: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in fetch_session_chats: {e}")
    return []


def send_message(session_id, question, token, file_data=None):
    """Send a chat message to the backend."""
    try:
        data = {"session_id": session_id, "question": question}
        headers = {"Authorization": f"Bearer {token}"}

        if file_data:
            res = requests.post(
                f"{backend_url}/chat/send_message",
                headers=headers,
                data=data,
                files=file_data,
                timeout=20,
            )
        else:
            res = requests.post(
                f"{backend_url}/chat/send_message",
                headers=headers,
                data=data,
                timeout=20,
            )

        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"send_message failed: {res.status_code} - {res.text}")
            return {"error": res.text, "status": res.status_code}

    except requests.RequestException as e:
        logger.error(f"Network error while sending message: {e}")
        return {"error": str(e), "status": 500}
    except Exception as e:
        logger.error(f"Unexpected error in send_message: {e}")
        return {"error": str(e), "status": 500}


# ---------- User Functions ----------
def login_user(user_email, user_password):
    """Login user."""
    try:
        payload = {"username": user_email, "password": user_password}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        res = requests.post(f"{backend_url}/user/login", data=payload, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"login_user failed: {res.status_code} - {res.text}")
            return {"error": res.text, "status": res.status_code}

    except requests.RequestException as e:
        logger.error(f"Network error during login: {e}")
        return {"error": str(e), "status": 500}
    except Exception as e:
        logger.error(f"Unexpected error in login_user: {e}")
        return {"error": str(e), "status": 500}


def register_user(username, user_email, user_password):
    """Register user."""
    try:
        payload = {"username": username, "user_email": user_email, "user_password": user_password}
        res = requests.post(f"{backend_url}/user/register", json=payload, timeout=10)

        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"register_user failed: {res.status_code} - {res.text}")
            return {"error": res.text, "status": res.status_code}

    except requests.RequestException as e:
        logger.error(f"Network error during register: {e}")
        return {"error": str(e), "status": 500}
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {e}")
        return {"error": str(e), "status": 500}


# ---------- Token Utility ----------
class TokenData:
    """Decode token and get data values from token."""

    def __init__(self, token: str):
        self.token = token
        try:
            self.decoded = jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            self.decoded = {}

    def is_token_expired(self) -> bool:
        """Check if token is expired."""
        try:
            exp = self.decoded.get("exp")
            if not exp:
                return True
            return datetime.now(timezone.utc).timestamp() > exp
        except Exception as e:
            logger.error(f"Error checking token expiry: {e}")
            return True

    def get_user_info(self) -> dict:
        """Get basic user info from token."""
        try:
            return {
                "username": self.decoded.get("username"),
                "email": self.decoded.get("email"),
                "user_id": self.decoded.get("user_id"),
            }
        except Exception as e:
            logger.error(f"Error extracting user info from token: {e}")
            return {}
