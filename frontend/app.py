import streamlit as st
import uuid
from utils import fetch_all_sessions, fetch_session_chats, send_message

st.title("Chat Bot")
chat_prompt = st.chat_input("Ask anything")

with st.sidebar:
    sidebar_title = st.title("Sidebar Menu")

    file_upload = st.file_uploader("Upload File:", type=["txt", "csv", "pdf", "png"])

    if "current_session" not in st.session_state:
        st.session_state["current_session"] = None
    new_chat_button = st.button("New Chat")
    if new_chat_button:
        new_id = str(uuid.uuid4())
        st.session_state["current_session"] = new_id

    choice = None
    all_sessions = fetch_all_sessions()

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
        session_chat = fetch_session_chats(choice)

        for chat in session_chat:
            st.markdown(
                f"""
                <div style="
                    background-color: #f9f9f9;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 12px;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                    position: relative;
                ">
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
        if file_upload is not None:
            st.markdown(f"**Question:** {chat_prompt}")
            files = {"file": (file_upload.name, file_upload.getvalue(), file_upload.type)}
            create_message = send_message(session_id=choice, question=chat_prompt, file_data=files)
            st.write(create_message)
        else:
            st.markdown(f"**Question:** {chat_prompt}")
            create_message = send_message(session_id=choice, question=chat_prompt)
            st.write(create_message)
except Exception as e:
    st.error(e)
