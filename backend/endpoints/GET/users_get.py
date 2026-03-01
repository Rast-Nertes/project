"""
GET /api/v1/users — User data retrieval
Access: admin (full list), any auth user (own profile)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Users
from schemas.users import UserOut
from middlewares.auth_middleware import get_current_user, require_admin

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Users = Depends(get_current_user)):
    """Текущий пользователь — данные своего профиля."""
    return current_user


@router.get("/", response_model=list[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Список всех пользователей (только admin)."""
    result = await db.execute(select(Users).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Получить пользователя по ID. Admin — любой; остальные — только себя."""
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
