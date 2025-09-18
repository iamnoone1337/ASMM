import asyncio
import backend.app.resolver as r

async def test_resolve_many_mocked(monkeypatch):
    def fake_sync(name):
        if name == "ok.example.com":
            return True, ["1.2.3.4"], ["A"]
        return False, [], []
    monkeypatch.setattr(r, "_resolve_sync", fake_sync)
    res = await r.resolve_many(["ok.example.com", "nope.example.com"], concurrency=5)
    assert res["ok.example.com"]["resolved"] is True
    assert res["ok.example.com"]["ips"] == ["1.2.3.4"]
    assert res["nope.example.com"]["resolved"] is False