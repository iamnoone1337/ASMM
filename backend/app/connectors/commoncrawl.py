# Minimal placeholder using Wayback only (Common Crawl indexers change often). This keeps modularity for later.
from typing import List, Dict

from .base import PassiveConnector

class CommonCrawlConnector(PassiveConnector):
    name = "commoncrawl"
    qps = 0.5

    async def fetch(self, domain: str, scope=None) -> List[Dict]:
        # For MVP, return empty list (non-fatal). Could be extended with CC index API.
        return []