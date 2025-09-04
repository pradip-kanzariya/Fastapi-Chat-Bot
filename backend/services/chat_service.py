import json
import numpy as np

def build_messages(retrieved_chats, new_question):
    """Generate message for llm."""
    messages = []
    
    for chat in retrieved_chats:
        if chat.file_data:
            messages.append({"role": "user","content": f"Previously the user uploaded this document:\n\n{chat.file_data}"})
        messages.append({"role": "user", "content": chat.user_question})
        messages.append({"role": "assistant", "content": chat.model_answer})
    
    messages.append({"role": "user", "content": new_question})
    return messages

def retrive_similar_chats(query_embeddings, stored_chats, top_k=3):
    """Retrive similar chats."""
    scored = []
    for chat in stored_chats:
        # Convert from JSON string → list[float] → numpy array
        embedding = json.loads(chat.embedding)
        embedding = np.array(embedding, dtype=np.float32)
        score = cosine_similarity(query_embeddings, embedding)
        scored.append((score, chat))
    scored.sort(key= lambda x: x[0], reverse=True)
    return [chat for _, chat in scored[:top_k]]

def cosine_similarity(a, b):
    """Check similarity of "a" and "b"."""
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
