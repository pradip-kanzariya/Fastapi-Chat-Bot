import boto3
import json
import logging
from backend.core.configuration import settings

logger = logging.getLogger(__name__)

class BedrockServices:
    """AWS bedrock session and client."""

    _session = None
    _client = None

    @classmethod
    def _init_client(cls):
        if cls._client is None:
            cls._session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_session_token=settings.AWS_SESSION_TOKEN,
                region_name=settings.AWS_REGION_NAME
            )
            cls._client = cls._session.client(service_name=settings.AWS_SERVICE_NAME)

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._init_client()
        return cls._client

    @classmethod
    def generate_embeddings(cls, text: str):
        client = cls.get_client()
        body = json.dumps({"inputText": text})
        try:
            response = client.invoke_model(
                modelId=settings.AWS_EMBEDDING_MODEL_ID,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response["body"].read())
            return result.get("embedding")
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
