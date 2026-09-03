import psycopg2

from src.config import settings


class DBConnection:
    def __enter__(self):
        self.conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
