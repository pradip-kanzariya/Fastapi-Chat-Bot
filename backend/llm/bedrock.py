import boto3
import os
from dotenv import load_dotenv
load_dotenv()

class Bedrock:
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name="us-east-1"
    )

    client = session.client(
        service_name="bedrock-runtime"
    )