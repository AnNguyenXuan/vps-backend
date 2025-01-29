from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.group_permission import GroupPermission
from app.schema.group_permission_schema import GroupPermissionCreate

async def create_group_permission(db: AsyncSession, group_permission: GroupPermissionCreate):
    new_group_permission = GroupPermission(**group_permission.dict())
    db.add(new_group_permission)
    await db.commit()
    await db.refresh(new_group_permission)
    return new_group_permission

async def get_group_permission_by_id(db: AsyncSession, group_permission_id: int):
    result = await db.execute(select(GroupPermission).where(GroupPermission.id == group_permission_id))
    return result.scalar_one_or_none()
