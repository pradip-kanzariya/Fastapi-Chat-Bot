import numpy as np
import json
from datetime import datetime

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrive_similar_chats(query_embeddings, stored_chats, top_k=3):
    scored = []
    for chat in stored_chats:
        # Convert from JSON string → list[float] → numpy array
        embedding = json.loads(chat.embedding)
        embedding = np.array(embedding, dtype=np.float32)
        score = cosine_similarity(query_embeddings, embedding)
        scored.append((score, chat))
    scored.sort(key= lambda x: x[0], reverse=True)
    return [chat for _, chat in scored[:top_k]]

def build_messages(retrieved_chats, new_question):
    messages = []
    
    for chat in retrieved_chats:
        if chat.file_data:
            messages.append({"role": "user","content": f"Previously the user uploaded this document:\n\n{chat.file_data}"})
        messages.append({"role": "user", "content": chat.user_question})
        messages.append({"role": "assistant", "content": chat.model_answer})
    
    messages.append({"role": "user", "content": new_question})
    return messages


def format_created_at(created_at: datetime) -> str:
    now = datetime.now().date()
    if created_at.date() == now:
        # Same day → only show time
        return f"Today {created_at.strftime('%H:%M:%S')}"
    else:
        # Different day → show full date and time
        return created_at.strftime("%Y-%m-%d %H:%M:%S")
    