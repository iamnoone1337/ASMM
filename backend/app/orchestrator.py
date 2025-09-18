import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from .models import Scan, ScanJob, Asset, AssetSource
from .normalizer import normalize_subdomain, in_scope, dedupe_merge
from .connectors.crtsh import CrtShConnector
from .connectors.chaos import ChaosConnector
from .connectors.securitytrails import SecurityTrailsConnector
from .connectors.wayback import WaybackConnector
from .connectors.commoncrawl import CommonCrawlConnector
from .connectors.bruteforce import generate_candidates, as_connector_output
from .resolver import resolve_many
from .config import settings

log = logging.getLogger("orchestrator")

def _active_enabled(token: Optional[str]) -> bool:
    return bool(settings.ACTIVE_SCAN_TOKEN and token and token == settings.ACTIVE_SCAN_TOKEN)

async def run_scan_pipeline(db: Session, scan_id: str, active_token: Optional[str] = None):
    scan: Scan = db.query(Scan).filter(Scan.id == scan_id).one()
    scan.status = "running"
    scan.started_at = datetime.utcnow()
    db.commit()

    connectors = [
        CrtShConnector(),
        ChaosConnector(),
        SecurityTrailsConnector(),
        WaybackConnector(),
        CommonCrawlConnector(),
    ]

    # Create per-connector scan jobs
    for c in connectors:
        job = ScanJob(scan_id=scan.id, connector=c.name, status="pending")
        db.add(job)
    db.commit()

    # parallel execution of connectors
    async def run_connector(c):
        job = db.query(ScanJob).filter(ScanJob.scan_id == scan.id, ScanJob.connector == c.name).one()
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        try:
            out = await c.safe_fetch(scan.domain, scope=scan.scope)
            job.status = "completed"
            job.finished_at = datetime.utcnow()
            db.commit()
            return out
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
            return []

    all_results = await asyncio.gather(*[run_connector(c) for c in connectors])
    flat_results = [item for sub in all_results for item in sub]

    # Bruteforce (active) if enabled by token and scan.bruteforce True
    if scan.bruteforce and _active_enabled(active_token):
        cands = generate_candidates(scan.domain, limit=settings.BRUTEFORCE_MAX_CANDIDATES)
        flat_results.extend(as_connector_output(cands))

    # Scope filter
    include = (scan.scope or {}).get("include")
    exclude = (scan.scope or {}).get("exclude")
    filtered = [r for r in flat_results if in_scope(r["subdomain"], scan.domain, include, exclude)]

    # Deduplicate and merge sources
    merged = dedupe_merge(filtered)

    # Optional resolution (active) only with token and scan.resolution True
    resolution_results = {}
    if scan.resolution and _active_enabled(active_token):
        names = list(merged.keys())
        resolution_results = await resolve_many(names, concurrency=settings.RESOLVER_MAX_CONCURRENCY)

    # Upsert into DB
    now = datetime.utcnow()
    for norm, rec in merged.items():
        asset: Asset = (
            db.query(Asset)
            .filter(Asset.domain == scan.domain, Asset.normalized == norm)
            .one_or_none()
        )
        ips = resolution_results.get(norm, {}).get("ips", [])
        rrtypes = resolution_results.get(norm, {}).get("rrtypes", [])
        resolved = resolution_results.get(norm, {}).get("resolved", False)

        if not asset:
            asset = Asset(
                domain=scan.domain,
                subdomain=rec["subdomain"],
                normalized=norm,
                resolved=resolved,
                ips=ips,
                rrtypes=rrtypes,
                first_seen=now,
                last_seen=now,
            )
            db.add(asset)
            db.flush()
        else:
            # update
            asset.last_seen = now
            asset.resolved = resolved or asset.resolved
            if ips:
                prev_ips = set(asset.ips or [])
                new_ips = sorted(list(prev_ips.union(set(ips))))
                asset.ips = new_ips
            if rrtypes:
                prev = set(asset.rrtypes or [])
                asset.rrtypes = sorted(list(prev.union(set(rrtypes))))

        # sources
        existing_sources = {s.source: s for s in asset.sources}
        for sname in rec["sources"]:
            srow = existing_sources.get(sname)
            if not srow:
                proof = rec.get("proofs", {}).get(sname)
                srow = AssetSource(asset_id=asset.id, source=sname, proof=proof or None, first_seen=now, last_seen=now)
                db.add(srow)
            else:
                srow.last_seen = now

    db.commit()

    scan.status = "completed"
    scan.finished_at = datetime.utcnow()
    db.commit()