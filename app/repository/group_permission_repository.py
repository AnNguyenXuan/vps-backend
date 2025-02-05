from sqlalchemy.future import select
from sqlalchemy import asc, func
from app.model.group_permission import GroupPermission
from app.configuration.database import AsyncSessionLocal


class GroupPermissionRepository:
    async def find_group_permission(self, group_id: int, permission_name: str) -> list:
        """
        Lấy danh sách quyền theo groupId và permissionName, ưu tiên bản ghi target_id = None
        (giả sử quan hệ giữa GroupPermission và Permission được định nghĩa qua thuộc tính `permission`
         và trường name của Permission là `name`).
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
