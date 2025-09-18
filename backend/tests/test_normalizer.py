from backend.app.normalizer import normalize_subdomain, in_scope, dedupe_merge

def test_normalize():
    assert normalize_subdomain("*.Sub.Example.com.") == "sub.example.com"
    assert normalize_subdomain("api.example.com") == "api.example.com"

def test_in_scope():
    assert in_scope("api.example.com", "example.com")
    assert not in_scope("api.bad.com", "example.com")
    assert in_scope("api.example.com", "example.com", include=[r"^api"])
    assert not in_scope("dev.example.com", "example.com", include=[r"^api"])
    assert not in_scope("api.example.com", "example.com", exclude=[r"^api"])

def test_dedupe_merge():
    items = [
        {"subdomain":"api.example.com","source":"crtsh","proof":{"id":1}},
        {"subdomain":"api.example.com","source":"chaos","proof":{"id":2}},
        {"subdomain":"API.example.com","source":"wayback","proof":{"id":3}},
    ]
    merged = dedupe_merge(items)
    assert "api.example.com" in merged
    assert set(merged["api.example.com"]["sources"]) == {"chaos","crtsh","wayback"}