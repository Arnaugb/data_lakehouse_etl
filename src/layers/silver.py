import io

import pandas as pd

from src.aws_client import get_s3_client
from src.config import settings


def process_bronze_to_silver(bronze_key: str):
    print(f"[INFO] Iniciando procesamiento Silver para: {bronze_key}")
    s3 = get_s3_client()

    print("[INFO] Leyendo datos desde Bronze S3 a memoria RAM...")
    response = s3.get_object(Bucket=settings.bronze_bucket, Key=bronze_key)
    csv_buffer = io.BytesIO(response["Body"].read())

    df = pd.read_csv(csv_buffer)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.dropna()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    execution_date = df["timestamp"].dt.date.iloc[0]
    year = execution_date.year
    month = f"{execution_date.month:02d}"
    day = f"{execution_date.day:02d}"

    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False, engine="pyarrow")

    parquet_buffer.seek(0)

    silver_key = f"processed_telemetry/year={year}/month={month}/day={day}/data.parquet"

    print(f"[INFO] Escribiendo formato Parquet en Silver: {silver_key}")
    s3.put_object(
        Bucket=settings.silver_bucket,
        Key=silver_key,
        Body=parquet_buffer.getvalue(),
    )
    print("[INFO] Capa Silver completada con éxito.")

    return silver_key
