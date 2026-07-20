import os

import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrock

load_dotenv()
os.environ["AWS_PROFILE"] = os.getenv("AWS_PROFILE", "codeplatoon")


def create_client(region="us-east-1"):
    """Create and return a Bedrock runtime client."""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=region,
    )


def create_llm(client, model_id="us.amazon.nova-lite-v1:0"):
    """Create and return a ChatBedrock LLM instance."""
    return ChatBedrock(
        model=model_id,
        client=client,
        model_kwargs={
            "max_tokens": 2000,
            "temperature": 0.9,
        },
    )
