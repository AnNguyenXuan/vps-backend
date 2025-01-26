# app/services/user_permission.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_permission_repository import create_user_permission, get_user_permission_by_id
from app.schema.user_permission_schema import UserPermissionCreate

async def create_new_user_permission(db: AsyncSession, user_permission: UserPermissionCreate):
    return await create_user_permission(db, user_permission)

async def fetch_user_permission_by_id(db: AsyncSession, user_permission_id: int):
    return await get_user_permission_by_id(db, user_permission_id)
