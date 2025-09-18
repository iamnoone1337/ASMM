import asyncio
import time

class TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: int):
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()
        self._lock = asyncio.Lock()

    async def take(self, tokens=1):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.timestamp
            self.timestamp = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            while self.tokens < tokens:
                await asyncio.sleep(max(0.01, (tokens - self.tokens) / self.rate))
                now = time.monotonic()
                elapsed = now - self.timestamp
                self.timestamp = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.tokens -= tokens