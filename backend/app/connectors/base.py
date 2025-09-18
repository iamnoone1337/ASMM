import asyncio
import json
import logging
import os
from typing import List, Dict, Optional
from ..config import settings
from ..rate_limiter import TokenBucket

log = logging.getLogger("connectors")

class PassiveConnector:
    name = "base"
    timeout = settings.CONNECTOR_TIMEOUT_SECONDS
    qps = 2.0

    def __init__(self):
        self.bucket = TokenBucket(rate_per_sec=self.qps, capacity=max(1, int(self.qps)))

    async def fetch(self, domain: str, scope: Optional[dict] = None) -> List[Dict]:
        raise NotImplementedError

    async def safe_fetch(self, domain: str, scope: Optional[dict] = None) -> List[Dict]:
        try:
            await self.bucket.take()
            return await asyncio.wait_for(self.fetch(domain, scope=scope), timeout=self.timeout)
        except Exception as e:
            log.warning(f"{self.name} connector failed: {e}")
            return []

    def save_raw(self, domain: str, data):
        try:
            os.makedirs(settings.RAW_STORAGE_DIR, exist_ok=True)
            path = os.path.join(settings.RAW_STORAGE_DIR, f"{self.name}_{domain}.json")
            with open(path, "w") as f:
                json.dump(data, f)
        except Exception:
            pass