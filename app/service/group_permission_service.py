from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.group_permission_repository import create_group_permission, get_group_permission_by_id
from app.schema.group_permission_schema import GroupPermissionCreate

async def create_new_group_permission(db: AsyncSession, group_permission: GroupPermissionCreate):
    return await create_group_permission(db, group_permission)

async def fetch_group_permission_by_id(db: AsyncSession, group_permission_id: int):
    return await get_group_permission_by_id(db, group_permission_id)
