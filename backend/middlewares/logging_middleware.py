"""
Insight IS — Logging Middleware (loguru + BaseHTTPMiddleware)
Logs every incoming request and outgoing response.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        # Log request
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"| client={request.client.host if request.client else 'unknown'}"
        )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
            raise

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            f"← {request.method} {request.url.path} "
            f"| status={response.status_code} | {elapsed:.1f}ms"
        )
        return response
