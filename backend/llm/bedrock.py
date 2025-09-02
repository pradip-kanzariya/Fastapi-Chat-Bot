import boto3
import json
import logging
from backend.configuration import settings

logger = logging.getLogger(__name__)

class Bedrock:
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION_NAME
        )
        self.client = self.session.client(service_name=settings.AWS_SERVICE_NAME)

    def generate_embeddings(self, text: str):
        body = json.dumps({"inputText": text})
        try:
            response = self.client.invoke_model(
                modelId=settings.AWS_EMBEDDING_MODEL_ID,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response["body"].read())
            return result.get("embedding")
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
