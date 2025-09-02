import streamlit as st
import uuid
import logging
from streamlit_cookies_manager import EncryptedCookieManager
from utils import fetch_all_sessions, fetch_session_chats, send_message, login_user, register_user, TokenData
from configuration import cookies

logger = logging.getLogger(__name__)

logger.info("App staring.")

cookies = EncryptedCookieManager(
    prefix="chat_app",
    password="super_secret_key",
)

if not cookies.ready():
    st.stop()

# Store JWT token in session state
if "token" not in st.session_state:
    st.session_state["token"] = cookies.get("token")

if not st.session_state["token"]:
    st.sidebar.title("Auth Menu")
    auth_choice = st.sidebar.radio("Choose action", ["Login", "Register"])

    if auth_choice == "Login":
        st.title("Login")
        input_email = st.text_input("Email")
        input_password = st.text_input("Password", type="password")

        if st.button("Login"):
            token = login_user(input_email, input_password)
            if token:
                cookies["token"] = token["access_token"]
                cookies.save()
                st.session_state["token"] = token["access_token"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:  # Register
        st.title("Register")
        register_username = st.text_input("Username")
        register_email = st.text_input("Email")
        register_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if register_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success = register_user(register_username, register_email, register_password)
                if success:
                    st.success("Registration successful! Please login now.")
                else:
                    st.error("Registration failed. Try another email.")

else:
    token_data = TokenData(st.session_state["token"])

    if token_data.is_token_expired():
        st.warning("Session expired. Please login again.")
        st.session_state["token"] = None
        cookies["token"] = ""
        cookies.save()
        st.rerun()

    st.title("Chat Bot")
    chat_prompt = st.chat_input("Ask anything")

    with st.sidebar:
        user_info = token_data.get_user_info()
        st.write(f"Welcome {user_info["username"]}")
        if st.button("Logout"):
            st.session_state["token"] = None
            cookies["token"] = ""
            cookies.save()
            st.rerun()

        st.subheader("Sidebar Menu")

        file_upload = st.file_uploader("Upload File:", type=["txt", "csv", "pdf", "png"])

        if "current_session" not in st.session_state:
            st.session_state["current_session"] = None

        if st.button("New Chat"):
            new_id = str(uuid.uuid4())
            st.session_state["current_session"] = new_id

        choice = None
        all_sessions = fetch_all_sessions(st.session_state["token"])

        if st.session_state["current_session"] and st.session_state["current_session"] not in all_sessions:
            all_sessions.insert(0, st.session_state["current_session"])

        if all_sessions:
            choice = st.radio("Chats", all_sessions, key="chat_selector")
        else:
            st.write("No chats found.")

    if choice == None:
        choice = str(uuid.uuid4())
        st.session_state["current_session"] = choice

    try:
        if choice:
            session_chat = fetch_session_chats(choice, st.session_state["token"])
            if session_chat:
                for chat in session_chat:
                    st.markdown(
                        f"""
                        <div style="background-color: #f9f9f9;
                                    padding: 15px; margin-bottom: 15px;
                                    border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                                    position: relative;">
                            <div style="position: absolute; top: 8px; right: 12px; font-size: 12px; color: gray;">
                                🕒 {chat['created_at']}
                            </div>
                            <p><b>Question:</b> {chat['question']}</p>
                            <p><b>Answer:</b> {chat['answer']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        if chat_prompt:
            st.markdown(f"**Question:** {chat_prompt}")
            if file_upload is not None:
                files = {"file": (file_upload.name, file_upload.getvalue(), file_upload.type)}
                create_message = send_message(choice, chat_prompt, st.session_state["token"], files)  # 🔑 pass token
            else:
                create_message = send_message(choice, chat_prompt, st.session_state["token"])  # 🔑 pass token

            st.write(create_message)
    except Exception as e:
        st.error(e)
