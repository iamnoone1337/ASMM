# Lightweight wrapper for RQ to call orchestrator
from sqlalchemy.orm import sessionmaker
from .db import engine, SessionLocal
from .orchestrator import run_scan_pipeline
import asyncio

def run_scan_job(scan_id: str, active_token: str | None):
    # new session per job
    session = SessionLocal()
    try:
        asyncio.run(run_scan_pipeline(session, scan_id, active_token))
    finally:
        session.close()