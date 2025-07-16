import boto3
from botocore.config import Config

from app.core.config import settings


async def get_s3_client() -> boto3.client:
    client = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_KEY_ID,
        config=Config(
            retries={"max_attempts": 5, "mode": "standard"},
            connect_timeout=5,
            read_timeout=60,
        ),
    )

    return client
