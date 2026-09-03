import boto3
from botocore.client import Config

from src.config import settings


def get_s3_client():
    """Devuelve un cleinte de S3 autenticado"""
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        config=Config(signature_version="s3v4"),
    )
