from typing import List, Dict

FAKE_CT = ["sub1.example.com", "dev.example.com"]
FAKE_CHAOS = ["api.example.com", "beta.example.com"]

async def fake_connector(domain: str) -> List[Dict]:
    out = []
    if domain.endswith("example.com"):
        for s in FAKE_CT:
            out.append({"subdomain": s, "source": "crtsh", "proof": {"fake": True}})
        for s in FAKE_CHAOS:
            out.append({"subdomain": s, "source": "chaos", "proof": {"fake": True}})
    return out