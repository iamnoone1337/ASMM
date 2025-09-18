import asyncio
from sqlalchemy.orm import Session
from backend.app.db import Base, engine, SessionLocal
from backend.app.models import Scan, Asset
from backend.app.orchestrator import run_scan_pipeline
from backend.app.connectors.fake import fake_connector
from backend.app.normalizer import normalize_subdomain

def setup_module(module):
    # create tables in a fresh SQLite memory DB if using SQLite URL
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

def test_pipeline_inserts_assets(monkeypatch):
    db: Session = SessionLocal()
    try:
        scan = Scan(domain="example.com", bruteforce=False, resolution=False, status="pending")
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Monkeypatch connector list to only use fake connector output
        async def fake_run(db, scan_id, token):
            # Manually insert results from fake connector
            from backend.app.normalizer import dedupe_merge, in_scope
            from backend.app.models import Asset, AssetSource
            from datetime import datetime
            data = asyncio.get_event_loop().run_until_complete(fake_connector("example.com"))
            merged = dedupe_merge(data)
            now = datetime.utcnow()
            for norm, rec in merged.items():
                asset = Asset(domain="example.com", subdomain=rec["subdomain"], normalized=norm,
                              resolved=False, ips=[], rrtypes=[], first_seen=now, last_seen=now)
                db.add(asset); db.flush()
                for sname in rec["sources"]:
                    from backend.app.models import AssetSource
                    db.add(AssetSource(asset_id=asset.id, source=sname, proof=rec.get("proofs",{}).get(sname), first_seen=now, last_seen=now))
            db.commit()
            scan.status = "completed"; db.commit()

        monkeypatch.setattr("backend.app.orchestrator.run_scan_pipeline", fake_run)

        # Actually run the pipeline that was monkeypatched
        asyncio.get_event_loop().run_until_complete(run_scan_pipeline(db, scan.id, None))

        assets = db.query(Asset).filter(Asset.domain == "example.com").all()
        norms = set(a.normalized for a in assets)
        assert "sub1.example.com" in norms
        assert "dev.example.com" in norms
        assert "api.example.com" in norms
        assert "beta.example.com" in norms
    finally:
        db.close()