from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.permission_repository import PermissionRepository
from app.schema.permission_schema import PermissionCreate

class PermissionService:
    def __init__(self):
        self.repository = PermissionRepository()

    async def create_new_permission(self, db: AsyncSession, permission: PermissionCreate):
        return await self.repository.create_permission(db, permission)

    async def fetch_permission_by_id(self, db: AsyncSession, permission_id: int):
        return await self.repository.get_permission_by_id(db, permission_id)
