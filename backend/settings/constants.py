"""
Insight IS — Application Constants
"""

from enum import Enum

# ── User Roles ────────────────────────────────
class Role(str, Enum):
    INVESTOR = "investor"
    TRADER = "trader"
    ADMIN = "admin"


# ── Subscription / Payment Statuses ───────────
class SubStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PayStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# ── Analysis ──────────────────────────────────
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Impact(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── Pagination ────────────────────────────────
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── Rate Limits ───────────────────────────────
# Requests per minute per IP
RATE_LIMIT_DEFAULT = 60
RATE_LIMIT_AUTH = 10

# ── News ──────────────────────────────────────
NEWS_FETCH_INTERVAL_SECONDS = 300   # 5 minutes
MAX_NEWS_PER_FETCH = 100
