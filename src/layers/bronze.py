import requests
from botocore.exceptions import ClientError

from src.aws_client import get_s3_client
from src.config import settings


def get_presigned_upload_url(object_key: str, expiration: int = 900) -> str:
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": settings.bronze_bucket, "Key": object_key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        print(f"[ERROR] AWS Boto3: {e}")
        raise


def simulate_client_upload(file_path: str, object_key: str):
    url = get_presigned_upload_url(object_key)
    print("[INFO] URL Presignada generada correctamente (expira en 15 min).")

    with open(file_path, "rb") as f:
        file_data = f.read()

    response = requests.put(url, data=file_data)

    if response.status_code == 200:
        print(f"[INFO] Archivo {file_path} subido a Bronze como '{object_key}'")
    else:
        print(
            f"[ERROR] Fallo HTTP en subida directa: {response.status_code} - {response.text}"
        )
