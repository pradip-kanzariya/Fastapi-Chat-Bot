from fastapi import HTTPException
import json
import logging
from backend.llm.bedrock_sevice import BedrockServices
from backend.core.configuration import settings

logger = logging.getLogger(__name__)


def call_llm(messages, max_tokens=2000, temperature=0.7, top_p=0.95, top_k=50):
    """Call AWS Bedrock LLM with given messages and return the generated text."""
    try:
        body = {
            "anthropic_version": settings.AWS_ANTHROPIC_VERSION,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "system": (
                "You are a helpful assistant. Use recent past chats if useful. "
                "Provide structured explanations, examples, code blocks, and summaries when needed."
            ),
            "messages": messages,
        }

        client = BedrockServices.get_client()
        response = client.invoke_model(
            modelId=settings.AWS_LLM_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))