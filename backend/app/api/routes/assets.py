from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ...db import get_db
from ...models import Asset, AssetSource
from ...schemas import AssetOut, AssetDetail

router = APIRouter()

@router.get("/assets", response_model=List[AssetOut])
def list_assets(
    domain: str,
    live: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Asset).filter(Asset.domain == domain)
    if live:
        q = q.filter(Asset.resolved == True)  # noqa: E712
    q = q.order_by(Asset.normalized).limit(limit).offset(offset)
    rows = q.all()
    results: List[AssetOut] = []
    for a in rows:
        sources = [s.source for s in a.sources]
        results.append(
            AssetOut(
                id=a.id,
                subdomain=a.subdomain,
                normalized=a.normalized,
                resolved=a.resolved,
                ips=a.ips or [],
                rrtypes=a.rrtypes or [],
                sources=sorted(list(set(sources))),
                first_seen=a.first_seen,
                last_seen=a.last_seen,
            )
        )
    return results

@router.get("/assets/{asset_id}", response_model=AssetDetail)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    a = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="not found")
    sources = [
        {"source": s.source, "first_seen": s.first_seen, "last_seen": s.last_seen, "proof": s.proof}
        for s in a.sources
    ]
    return AssetDetail(
        id=a.id,
        domain=a.domain,
        subdomain=a.subdomain,
        normalized=a.normalized,
        resolved=a.resolved,
        ips=a.ips or [],
        rrtypes=a.rrtypes or [],
        sources=sorted(list(set([s["source"] for s in sources]))),
        source_details=sources,
        first_seen=a.first_seen,
        last_seen=a.last_seen,
    )

@router.get("/assets/export.csv")
def export_csv(domain: str, db: Session = Depends(get_db)):
    import csv, io
    q = db.query(Asset).filter(Asset.domain == domain).order_by(Asset.normalized)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["subdomain","normalized","resolved","ips","sources","first_seen","last_seen"])
    for a in q:
        sources = sorted(list(set([s.source for s in a.sources])))
        writer.writerow([
            a.subdomain, a.normalized, "true" if a.resolved else "false",
            ";".join(a.ips or []),
            ";".join(sources),
            a.first_seen.isoformat()+"Z" if a.first_seen else "",
            a.last_seen.isoformat()+"Z" if a.last_seen else "",
        ])
    data = buf.getvalue()
    return Response(content=data, media_type="text/csv")

@router.get("/assets/graph.json")
def graph_json(domain: str, db: Session = Depends(get_db)):
    # Simple JSON-LD-like export: nodes (assets) and edges (asset->domain)
    assets = db.query(Asset).filter(Asset.domain == domain).all()
    graph = {
        "@context": "https://schema.org",
        "@type": "Graph",
        "domain": domain,
        "nodes": [{"id": a.id, "type": "Subdomain", "name": a.normalized, "resolved": a.resolved} for a in assets],
        "edges": [{"from": a.id, "to": domain, "type": "belongs_to"} for a in assets],
    }
    return graph