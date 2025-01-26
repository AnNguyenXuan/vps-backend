# app/repository/group.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.group import Group
from app.schema.group_schema import GroupCreate

async def create_group(db: AsyncSession, group: GroupCreate):
    new_group = Group(**group.dict())
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)
    return new_group

async def get_groups(db: AsyncSession):
    result = await db.execute(select(Group))
    return result.scalars().all()

async def get_group_by_id(db: AsyncSession, group_id: int):
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()
