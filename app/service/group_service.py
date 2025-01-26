# app/services/group.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.group_repository import create_group, get_groups, get_group_by_id
from app.schema.group_schema import GroupCreate

async def create_new_group(db: AsyncSession, group: GroupCreate):
    return await create_group(db, group)

async def fetch_all_groups(db: AsyncSession):
    return await get_groups(db)

async def fetch_group_by_id(db: AsyncSession, group_id: int):
    return await get_group_by_id(db, group_id)
