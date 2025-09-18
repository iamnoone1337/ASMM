import httpx
from typing import List, Dict
from .base import PassiveConnector
from ..normalizer import normalize_subdomain

class CrtShConnector(PassiveConnector):
    name = "crtsh"
    qps = 1.0

    async def fetch(self, domain: str, scope=None) -> List[Dict]:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers={"User-Agent": "ASM/1.0"})
            if r.status_code != 200:
                return []
            try:
                data = r.json()
            except Exception:
                # crt.sh sometimes returns text/html; fallback to empty
                data = []
        out = []
        for row in data:
            name = row.get("name_value") or ""
            # may contain multiple lines
            for candidate in name.splitlines():
                n = normalize_subdomain(candidate)
                if not n:
                    continue
                out.append({"subdomain": n, "source": self.name, "proof": {"crtsh_id": row.get("id")}})
        self.save_raw(domain, out)
        return out