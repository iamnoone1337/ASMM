import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, UniqueConstraint, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .db import Base

def _json_type():
    # JSONB if Postgres, else JSON for SQLite
    try:
        import psycopg2  # noqa
        return JSONB
    except Exception:
        return JSON

class Owner(Base):
    __tablename__ = "owners"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String, nullable=False, index=True)
    scope = Column(_json_type(), nullable=True)
    bruteforce = Column(Boolean, default=False)
    resolution = Column(Boolean, default=False)
    notify = Column(Boolean, default=False)
    status = Column(String, default="pending")
    error = Column(Text, nullable=True)
    requested_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    jobs = relationship("ScanJob", back_populates="scan", cascade="all, delete-orphan")

class ScanJob(Base):
    __tablename__ = "scan_jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    connector = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending/running/completed/failed
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    scan = relationship("Scan", back_populates="jobs")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String, index=True, nullable=False)
    subdomain = Column(String, nullable=False)
    normalized = Column(String, index=True, nullable=False)
    resolved = Column(Boolean, default=False)
    ips = Column(_json_type(), nullable=True)  # list of IPs
    rrtypes = Column(_json_type(), nullable=True)  # e.g., ["A","AAAA","CNAME"]
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint("domain", "normalized", name="uq_domain_normalized"),
        Index("ix_assets_domain_normalized", "domain", "normalized"),
    )
    sources = relationship("AssetSource", back_populates="asset", cascade="all, delete-orphan")

class AssetSource(Base):
    __tablename__ = "asset_sources"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    source = Column(String, nullable=False)  # e.g., "crtsh"
    proof = Column(_json_type(), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    asset = relationship("Asset", back_populates="sources")
    __table_args__ = (
        Index("ix_asset_sources_asset_id_source", "asset_id", "source"),
    )