import os
import json
from dotenv import load_dotenv
from backend.llm.bedrock import Bedrock

load_dotenv()

def generate_embeddings(text: str):
    body = json.dumps({
        "inputText": text
    })

    response = Bedrock.client.invoke_model(
        modelId=os.getenv("AWS_EMBEDDING_MODEL_ID"),
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["embedding"]