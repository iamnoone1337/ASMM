from typing import List, Dict
import os
from ..config import settings

def generate_candidates(domain: str, limit: int = None) -> List[str]:
    path = settings.WORDLIST_PATH
    words = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                w = line.strip()
                if not w or w.startswith("#"):
                    continue
                words.append(w)
                if limit and len(words) >= limit:
                    break
    else:
        # Fallback
        words = ["dev","staging","stage","test","api","www","admin"]
    candidates = [f"{w}.{domain}" for w in words]
    if limit:
        candidates = candidates[:limit]
    return candidates

def as_connector_output(candidates: List[str]) -> List[Dict]:
    return [{"subdomain": c, "source": "bruteforce", "proof": {"wordlist": True}} for c in candidates]