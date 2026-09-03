from src.layers.bronze import simulate_client_upload


def run_pipeline():
    print("[INFO] Iniciando Pipeline ETL Lakehouse")

    simulate_client_upload(
        file_path="data/raw_sample.csv",
        object_key="raw_telemetry/2026-09-03/session_01.csv",
    )


if __name__ == "__main__":
    run_pipeline()
