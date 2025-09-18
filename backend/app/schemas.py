from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ScopeConfig(BaseModel):
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None

class ScanCreate(BaseModel):
    domain: str
    scope: Optional[ScopeConfig] = None
    bruteforce: bool = False
    resolution: bool = False
    notify: bool = False
    active_token: Optional[str] = None

class ScanStatus(BaseModel):
    id: str
    domain: str
    status: str
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    jobs: List[Dict[str, Any]] = Field(default_factory=list)

class AssetOut(BaseModel):
    id: str
    subdomain: str
    normalized: str
    resolved: bool
    ips: List[str] = []
    rrtypes: List[str] = []
    sources: List[str] = []
    first_seen: datetime
    last_seen: datetime

class AssetDetail(AssetOut):
    domain: str
    source_details: List[Dict[str, Any]] = []