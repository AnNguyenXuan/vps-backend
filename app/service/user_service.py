# app/services/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repository import create_user, get_user_by_id
from app.schema.user_schema import UserCreate

async def create_new_user(db: AsyncSession, user: UserCreate):
    return await create_user(db, user)

async def fetch_user_by_id(db: AsyncSession, user_id: int):
    return await get_user_by_id(db, user_id)
