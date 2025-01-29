from sqlalchemy.ext.asyncio import AsyncSession
from app.model.group_member import GroupMember
from app.schema.group_member_schema import GroupMemberCreate

class GroupMemberRepository:
    async def create_group_member(self, db: AsyncSession, group_member: GroupMemberCreate):
        new_group_member = GroupMember(**group_member.dict())
        db.add(new_group_member)
        await db.commit()
        return new_group_member
