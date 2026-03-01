"""
Insight IS — FastAPI Auth Middleware / Dependency
JWT verification using python-jose.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import decode_access_token
from database.connection import get_db
from database.models import Users
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Users:
    """Dependency: decode JWT and return the authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    result = await db.execute(select(Users).where(Users.id == int(user_id)))
    user = result.scalars().first()

    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден или деактивирован")

    return user


def require_role(*roles: str):
    """Dependency factory: restrict access to specific roles."""
    async def role_checker(current_user: Users = Depends(get_current_user)) -> Users:
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется роль: {', '.join(roles)}",
            )
        return current_user
    return role_checker


# Convenience shortcuts
require_admin = require_role("admin")
require_investor_or_trader = require_role("investor", "trader", "admin")
