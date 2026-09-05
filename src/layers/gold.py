import io
import logging

import pandas as pd
from psycopg2.extras import execute_values

from src.aws_client import get_s3_client
from src.config import settings
from src.db_client import DBConnection
from src.schemas import WeeklyTrainingAgg

logger = logging.getLogger()


def process_silver_to_gold(silver_key: str):
    logger.info(f"Iniciando procesamiento Gold para: {silver_key}")
    s3 = get_s3_client()

    response = s3.get_object(Bucket=settings.silver_bucket, Key=silver_key)
    parquet_buffer = io.BytesIO(response["Body"].read())

    df = pd.read_parquet(parquet_buffer)

    df["week_start"] = (
        df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time).dt.date
    )

    agg_df = (
        df.groupby(["user_id", "week_start"])
        .agg(
            total_distance_m=("distance_m", "sum"),
            avg_heart_rate=("heart_rate", "mean"),
        )
        .reset_index()
    )

    valid_records = []
    for _, row in agg_df.iterrows():
        try:
            record = WeeklyTrainingAgg(**row.to_dict())
            valid_records.append(
                (
                    record.user_id,
                    record.week_start,
                    record.total_distance_m,
                    record.avg_heart_rate,
                )
            )
        except Exception as e:
            logger.error(f"Error de validación Pydantic en fila: {e}")
            raise

    insert_query = """
        INSERT INTO weekly_training_metrics (user_id, week_start, total_distance_m, avg_heart_rate)
        VALUES %s
        ON CONFLICT (user_id, week_start) 
        DO UPDATE SET 
            total_distance_m = EXCLUDED.total_distance_m,
            avg_heart_rate = EXCLUDED.avg_heart_rate;
    """

    with DBConnection() as conn, conn.cursor() as cursor:
        try:
            execute_values(cursor, insert_query, valid_records)
            conn.commit()
            logger.info(
                f"Transacción exitosa: {len(valid_records)} registros insertados en RDS."
            )
        except Exception as e:
            conn.rollback()
            logger.error(
                f"Fallo en inserción RDS. Haciendo ROLLBACK de la transacción. Error: {e}"
            )
            raise
