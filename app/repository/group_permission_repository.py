# repository/group_permission_repository.py
from sqlalchemy.future import select
from sqlalchemy import asc
from app.model.group_permission import GroupPermission
from app.core.database import AsyncSessionLocal

class GroupPermissionRepository:
    async def find_group_permission(self, group_id: int, permission_name: str) -> list:
        """
        Lấy danh sách GroupPermission theo group_id và permission_name,
        ưu tiên bản ghi có target_id = None (sắp xếp tăng dần theo target_id).
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupPermission)
                .join(GroupPermission.permission)
                .where(GroupPermission.group_id == group_id)
                .where(GroupPermission.permission.has(name=permission_name))
                .order_by(asc(GroupPermission.target_id))
            )
            return result.scalars().all()

    async def find_by_group(self, group) -> list:
        """
        Lấy danh sách GroupPermission theo Group.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupPermission).where(GroupPermission.group_id == group.id)
            )
            return result.scalars().all()

    async def find_one_by_group_and_permission(self, group, permission) -> GroupPermission:
        """
        Tìm một bản ghi GroupPermission dựa vào Group và Permission.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupPermission).where(
                    GroupPermission.group_id == group.id,
                    GroupPermission.permission_id == permission.id
                )
            )
            return result.scalar_one_or_none()

    async def bulk_insert(self, group_permissions: list) -> None:
        """
        Thêm nhiều bản ghi GroupPermission trong cùng một phiên giao dịch.
        """
        async with AsyncSessionLocal() as session:
            session.add_all(group_permissions)
            await session.commit()

    async def bulk_update(self, group_permissions: list) -> None:
        """
        Cập nhật nhiều bản ghi GroupPermission trong cùng một phiên giao dịch.
        (Ở đây, các đối tượng đã được thay đổi thuộc tính; chỉ cần add lại và commit.)
        """
        async with AsyncSessionLocal() as session:
            for gp in group_permissions:
                session.add(gp)
            await session.commit()

    async def bulk_delete(self, group_permissions: list) -> None:
        """
        Xóa nhiều bản ghi GroupPermission trong cùng một phiên giao dịch.
        """
        async with AsyncSessionLocal() as session:
            for gp in group_permissions:
                await session.delete(gp)
            await session.commit()
