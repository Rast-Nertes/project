"""
Insight IS — Throttle / Rate-Limit Middleware
Simple in-memory sliding-window rate limiter (60 req/min per IP by default).
For production consider Redis-backed SlowAPI.
"""

import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from settings.constants import RATE_LIMIT_DEFAULT


class ThrottleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_DEFAULT):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.window = 60  # seconds
        # ip -> deque of timestamps
        self._store: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Skip healthcheck
        if request.url.path in ("/", "/health"):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.time()
        queue = self._store[ip]

        # Evict old timestamps outside the window
        while queue and queue[0] < now - self.window:
            queue.popleft()

        if len(queue) >= self.rpm:
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Повторите через минуту."},
            )

        queue.append(now)
        return await call_next(request)
