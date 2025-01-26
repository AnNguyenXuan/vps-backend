# app/services/group_member.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.group_member_repository import create_group_member
from app.schema.group_member_schema import GroupMemberCreate

async def add_user_to_group(db: AsyncSession, group_member: GroupMemberCreate):
    return await create_group_member(db, group_member)
