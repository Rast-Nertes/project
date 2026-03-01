"""
POST /api/v1/users — Create user (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Users
from schemas.users import UserCreate, UserOut
from services.auth_service import hash_password
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Создать пользователя (только admin — Ф)."""
    result = await db.execute(
        select(Users).where((Users.email == data.email) | (Users.username == data.username))
    )
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="Email или username уже заняты")

    user = Users(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
