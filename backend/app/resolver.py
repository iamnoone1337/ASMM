import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple
import dns.resolver
from .config import settings

resolver = dns.resolver.Resolver(configure=True)
resolver.timeout = 3.0
resolver.lifetime = 3.0

_executor = ThreadPoolExecutor(max_workers=settings.RESOLVER_MAX_CONCURRENCY)

def _resolve_sync(name: str) -> Tuple[bool, List[str], List[str]]:
    ips = []
    rrtypes = []
    try:
        answers = resolver.resolve(name, "A", raise_on_no_answer=False)
        if answers.rrset:
            ips.extend([rdata.address for rdata in answers])
            rrtypes.append("A")
    except Exception:
        pass
    try:
        answers = resolver.resolve(name, "AAAA", raise_on_no_answer=False)
        if answers.rrset:
            ips.extend([rdata.address for rdata in answers])
            rrtypes.append("AAAA")
    except Exception:
        pass
    try:
        answers = resolver.resolve(name, "CNAME", raise_on_no_answer=False)
        if answers.rrset:
            rrtypes.append("CNAME")
    except Exception:
        pass
    return (len(ips) > 0 or "CNAME" in rrtypes, list(sorted(set(ips))), rrtypes)

async def resolve_many(names: List[str], concurrency: int = None) -> Dict[str, Dict]:
    concurrency = concurrency or settings.RESOLVER_MAX_CONCURRENCY
    sem = asyncio.Semaphore(concurrency)
    results: Dict[str, Dict] = {}

    async def _wrap(n: str):
        async with sem:
            resolved, ips, rrtypes = await asyncio.get_event_loop().run_in_executor(_executor, _resolve_sync, n)
            results[n] = {"resolved": resolved, "ips": ips, "rrtypes": rrtypes}

    await asyncio.gather(*[_wrap(name) for name in names])
    return results