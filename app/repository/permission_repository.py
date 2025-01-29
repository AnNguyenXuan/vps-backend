from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.permission import Permission
from app.schema.permission_schema import PermissionCreate

class PermissionRepository:
    async def create_permission(self, db: AsyncSession, permission: PermissionCreate):
        new_permission = Permission(**permission.dict())
        db.add(new_permission)
        await db.commit()
        await db.refresh(new_permission)
        return new_permission

    async def get_permission_by_id(self, db: AsyncSession, permission_id: int):
        result = await db.execute(select(Permission).where(Permission.id == permission_id))
        return result.scalar_one_or_none()
