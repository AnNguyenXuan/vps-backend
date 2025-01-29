from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.group_member_repository import GroupMemberRepository
from app.schema.group_member_schema import GroupMemberCreate

class GroupMemberService:
    def __init__(self):
        self.repository = GroupMemberRepository()

    async def add_user_to_group(self, db: AsyncSession, group_member: GroupMemberCreate):
        return await self.repository.create_group_member(db, group_member)
