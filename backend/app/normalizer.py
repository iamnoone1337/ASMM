import re

def normalize_subdomain(name: str) -> str:
    if not name:
        return ""
    n = name.strip().lower().rstrip(".")
    n = re.sub(r"^\*\.", "", n)  # remove wildcard
    return n

def in_scope(name: str, domain: str, include=None, exclude=None) -> bool:
    # Ensure it ends with .domain or equals domain
    name = normalize_subdomain(name)
    domain = normalize_subdomain(domain)
    if not (name == domain or name.endswith("." + domain)):
        return False
    if include:
        ok = any(re.search(pat, name) for pat in include)
        if not ok:
            return False
    if exclude:
        if any(re.search(pat, name) for pat in exclude):
            return False
    return True

def dedupe_merge(results):
    """
    results: list of dicts with keys: subdomain, source, proof
    returns dict normalized -> merged record with sources and proofs
    """
    merged = {}
    for r in results:
        norm = normalize_subdomain(r["subdomain"])
        if norm not in merged:
            merged[norm] = {"subdomain": r["subdomain"], "normalized": norm, "sources": set(), "proofs": {}}
        merged[norm]["sources"].add(r["source"])
        if r.get("proof") is not None:
            merged[norm]["proofs"].setdefault(r["source"], []).append(r["proof"])
    # finalize
    for k in list(merged.keys()):
        merged[k]["sources"] = sorted(list(merged[k]["sources"]))
    return merged