from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.user_permission import UserPermission
from app.schema.user_permission_schema import UserPermissionCreate

async def create_user_permission(db: AsyncSession, user_permission: UserPermissionCreate):
    new_user_permission = UserPermission(**user_permission.dict())
    db.add(new_user_permission)
    await db.commit()
    await db.refresh(new_user_permission)
    return new_user_permission

async def get_user_permission_by_id(db: AsyncSession, user_permission_id: int):
    result = await db.execute(select(UserPermission).where(UserPermission.id == user_permission_id))
    return result.scalar_one_or_none()
