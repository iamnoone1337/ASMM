import httpx
from typing import List, Dict
from .base import PassiveConnector
from ..config import settings

class ChaosConnector(PassiveConnector):
    name = "chaos"
    qps = 2.0

    async def fetch(self, domain: str, scope=None) -> List[Dict]:
        if not settings.CHAOS_API_KEY:
            # Mocked fallback
            sample = ["api." + domain, "beta." + domain]
            out = [{"subdomain": s, "source": self.name, "proof": {"mock": True}} for s in sample]
            self.save_raw(domain, out)
            return out
        url = f"https://dns.projectdiscovery.io/dns/{domain}/subdomains"
        headers = {"Authorization": settings.CHAOS_API_KEY, "User-Agent": "ASM/1.0"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
        subs = data.get("subdomains", [])
        out = [{"subdomain": f"{s}.{domain}" if not s.endswith(domain) else s, "source": self.name, "proof": {"raw": s}} for s in subs]
        self.save_raw(domain, out)
        return out