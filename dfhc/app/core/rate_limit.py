"""Per-process login/refresh limiter. Use an edge/shared limiter for multiple workers."""
from collections import OrderedDict, deque
from threading import Lock
from time import monotonic
from fastapi import HTTPException, Request


class AuthRateLimiter:
    def __init__(self, limit: int = 10, window: int = 60):
        self.limit = limit
        self.window = window
        self.attempts = OrderedDict()
        self.lock = Lock()

    def check(self, request: Request) -> None:
        # Do not trust caller-controlled X-Forwarded-For headers.
        key = request.client.host if request.client else "unknown"
        now = monotonic()
        with self.lock:
            while self.attempts and now - next(iter(self.attempts.values()))[-1] >= self.window:
                self.attempts.popitem(last=False)
            bucket = self.attempts.setdefault(key, deque())
            self.attempts.move_to_end(key)
            while bucket and now - bucket[0] >= self.window:
                bucket.popleft()
            if len(bucket) >= self.limit:
                raise HTTPException(status_code=429, detail="Too many authentication attempts", headers={"Retry-After": str(self.window)})
            bucket.append(now)
            if len(self.attempts) > 10000:
                self.attempts.popitem(last=False)


auth_rate_limiter = AuthRateLimiter()
