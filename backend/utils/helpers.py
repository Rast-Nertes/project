"""
Insight IS — General Helpers
"""

from typing import TypeVar, Type
from math import ceil

T = TypeVar("T")


def paginate(query_result: list, page: int, page_size: int) -> dict:
    """
    Simple pagination helper.
    Returns: {items, total, page, page_size, total_pages}
    """
    total = len(query_result)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": query_result[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": ceil(total / page_size) if total > 0 else 0,
    }