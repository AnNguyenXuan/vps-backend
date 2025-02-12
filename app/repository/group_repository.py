from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.database import AsyncSessionLocal
from app.model.group import Group
from app.core.exceptions import DuplicateDataError

class GroupRepository:
    async def create_group(self, new_group: Group):
        """Tạo nhóm mới với xử lý lỗi trùng dữ liệu"""
        async with AsyncSessionLocal() as db:
            try:
                db.add(new_group)
                await db.commit()
                await db.refresh(new_group)
                return new_group
            except IntegrityError:
                await db.rollback()
                raise DuplicateDataError("Group name already exists")

    async def get_group_by_id(self, group_id: int):
        """Lấy nhóm theo ID"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Group).where(Group.id == group_id))
            return result.scalar_one_or_none()

    async def get_group_by_name(self, name: str):
        """Lấy nhóm theo tên"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Group).where(Group.name == name))
            return result.scalar_one_or_none()

    async def get_groups_paginated(self, page: int, limit: int):
        """Lấy danh sách nhóm với phân trang"""
        async with AsyncSessionLocal() as db:
            offset = (page - 1) * limit
            result = await db.execute(
                select(Group)
                .order_by(Group.id.asc())
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()

    async def update_group(self, group: Group):
        """Cập nhật thông tin nhóm"""
        async with AsyncSessionLocal() as db:
            db.add(group)
            await db.commit()
            await db.refresh(group)
            return group

    async def delete_group(self, group: Group) -> bool:
        """Xóa nhóm và trả về True nếu thành công, False nếu thất bại"""
        async with AsyncSessionLocal() as db:
            try:
                await db.delete(group)
                await db.commit()
                return True
            except SQLAlchemyError:
                await db.rollback()
                return False
