from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rq import Queue
from redis import Redis
from ...schemas import ScanCreate, ScanStatus
from ...models import Scan, ScanJob
from ...db import get_db
from ...config import settings
from ...utils import utcnow

router = APIRouter()

def get_queue():
    redis = Redis.from_url(settings.REDIS_URL)
    return Queue(settings.RQ_QUEUE_NAME, connection=redis)

@router.post("/scan", response_model=dict)
def start_scan(payload: ScanCreate, db: Session = Depends(get_db)):
    # Passive by default; active only if token matches
    active_allowed = bool(settings.ACTIVE_SCAN_TOKEN and payload.active_token == settings.ACTIVE_SCAN_TOKEN)
    scan = Scan(
        domain=payload.domain.strip().lower(),
        scope=payload.scope.dict() if payload.scope else None,
        bruteforce=payload.bruteforce and active_allowed,
        resolution=payload.resolution and active_allowed,
        notify=payload.notify,
        status="pending",
        created_at=utcnow(),
        requested_by=None,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    q = get_queue()
    # Enqueue the orchestrator method; we import lazily to avoid circular deps in worker
    job = q.enqueue("backend.app.worker_entry.run_scan_job", scan.id, payload.active_token, job_timeout=1800)

    return {"job_id": job.id, "scan_id": scan.id}

@router.get("/scan/{scan_id}", response_model=ScanStatus)
def scan_status(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="scan not found")
    jobs = db.query(ScanJob).filter(ScanJob.scan_id == scan_id).all()
    return ScanStatus(
        id=scan.id,
        domain=scan.domain,
        status=scan.status,
        error=scan.error,
        created_at=scan.created_at,
        started_at=scan.started_at,
        finished_at=scan.finished_at,
        jobs=[{"connector": j.connector, "status": j.status, "error": j.error, "started_at": j.started_at, "finished_at": j.finished_at} for j in jobs],
    )