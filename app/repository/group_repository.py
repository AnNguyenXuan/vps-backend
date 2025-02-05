from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.configuration.database import AsyncSessionLocal
from app.model.group import Group

class GroupRepository:
    async def create_group(self, group_data: dict):
        """ Tạo nhóm mới """
        async with AsyncSessionLocal() as db:
            new_group = Group(**group_data)
            db.add(new_group)
            await db.commit()
            await db.refresh(new_group)
            return new_group

    async def get_group_by_id(self, group_id: int):
        """ Lấy nhóm theo ID """
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Group).where(Group.id == group_id))
            return result.scalar_one_or_none()

    async def get_group_by_name(self, name: str):
        """ Lấy nhóm theo tên """
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Group).where(Group.name == name))
            return result.scalar_one_or_none()

    async def get_groups_paginated(self, page: int, limit: int):
        """ Lấy danh sách nhóm với phân trang """
        async with AsyncSessionLocal() as db:
            offset = (page - 1) * limit
            result = await db.execute(
                select(Group)
                .order_by(Group.id.asc())
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()

    async def update_group(self, group_id: int, group_data: dict):
        """ Cập nhật thông tin nhóm """
        async with AsyncSessionLocal() as db:
            group = await self.get_group_by_id(group_id)
            if not group:
                return None
            
            for key, value in group_data.items():
                setattr(group, key, value)
            
            await db.commit()
            await db.refresh(group)
            return group

    async def delete_group(self, group_id: int):
        """ Xóa nhóm """
        async with AsyncSessionLocal() as db:
            group = await self.get_group_by_id(group_id)
            if not group:
                return False
            
            await db.delete(group)
            await db.commit()
            return True
