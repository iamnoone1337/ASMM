import time
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from .config import settings

DATABASE_URL = settings.DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args if connect_args else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _wait_for_service():
    # Best effort wait used in Docker entrypoints
    if DATABASE_URL.startswith("sqlite"):
        return
    import psycopg2
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL.replace("+psycopg2", ""))
    host = parsed.hostname
    port = parsed.port or 5432
    while True:
        try:
            conn = psycopg2.connect(
                dbname=parsed.path.lstrip("/"),
                user=parsed.username,
                password=parsed.password,
                host=host,
                port=port,
            )
            conn.close()
            break
        except Exception:
            print("Waiting for Postgres...", flush=True)
            time.sleep(2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    if args.wait:
        _wait_for_service()