# app/services/permission.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.permission_repository import create_permission, get_permission_by_id
from app.schema.permission_schema import PermissionCreate

async def create_new_permission(db: AsyncSession, permission: PermissionCreate):
    return await create_permission(db, permission)

async def fetch_permission_by_id(db: AsyncSession, permission_id: int):
    return await get_permission_by_id(db, permission_id)
