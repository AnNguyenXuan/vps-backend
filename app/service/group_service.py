from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.group_repository import GroupRepository
from app.schema.group_schema import GroupCreate

class GroupService:
    def __init__(self):
        self.repository = GroupRepository()

    async def create_new_group(self, db: AsyncSession, group: GroupCreate):
        return await self.repository.create_group(db, group)

    async def fetch_all_groups(self, db: AsyncSession):
        return await self.repository.get_groups(db)

    async def fetch_group_by_id(self, db: AsyncSession, group_id: int):
        return await self.repository.get_group_by_id(db, group_id)
