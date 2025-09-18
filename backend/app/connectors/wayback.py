import httpx
from typing import List, Dict
from urllib.parse import urlparse
from .base import PassiveConnector

class WaybackConnector(PassiveConnector):
    name = "wayback"
    qps = 1.0

    async def fetch(self, domain: str, scope=None) -> List[Dict]:
        # Wayback CDX API
        url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey"
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers={"User-Agent": "ASM/1.0"})
            if r.status_code != 200:
                return []
            data = r.json()
        out = []
        for row in data[1:] if data and isinstance(data, list) else []:
            try:
                u = urlparse(row[0])
                host = u.hostname or ""
                if host:
                    out.append({"subdomain": host, "source": self.name, "proof": {"url": row[0]}})
            except Exception:
                continue
        self.save_raw(domain, out)
        return out