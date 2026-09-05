import logging

import botocore
import psycopg2

from src.layers.bronze import simulate_client_upload
from src.layers.gold import process_silver_to_gold
from src.layers.silver import process_bronze_to_silver

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


def run_pipeline():
    logger.info("[INFO] Iniciando Pipeline ETL Lakehouse")

    bronze_key = "raw_telemetry/2026-09-03/session_01.csv"

    try:
        simulate_client_upload(
            file_path="data/raw_sample.csv",
            object_key=bronze_key,
        )

        silver_key = process_bronze_to_silver(bronze_key)

        process_silver_to_gold(silver_key)

        logger.info("Pipeline finalizado con éxito en todas sus capas.")
    except (botocore.exceptions.ClientError, psycopg2.Error, ValueError) as e:
        logger.fatal(f"Ejecución del pipeline abortada por error crítico: {e}")


if __name__ == "__main__":
    run_pipeline()
