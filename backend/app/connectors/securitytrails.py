import httpx
from typing import List, Dict
from .base import PassiveConnector
from ..config import settings

class SecurityTrailsConnector(PassiveConnector):
    name = "securitytrails"
    qps = 1.0

    async def fetch(self, domain: str, scope=None) -> List[Dict]:
        if not settings.SECURITYTRAILS_API_KEY:
            # Mocked fallback
            sample = ["dev." + domain]
            out = [{"subdomain": s, "source": self.name, "proof": {"mock": True}} for s in sample]
            self.save_raw(domain, out)
            return out
        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        headers = {"APIKEY": settings.SECURITYTRAILS_API_KEY, "User-Agent": "ASM/1.0"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
        subs = data.get("subdomains", [])
        out = [{"subdomain": f"{s}.{domain}", "source": self.name, "proof": {"raw": s}} for s in subs]
        self.save_raw(domain, out)
        return out