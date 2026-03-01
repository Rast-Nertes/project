"""
Insight IS — Pydantic Schemas: Auth
"""

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    role: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str
