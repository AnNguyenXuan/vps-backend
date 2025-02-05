from sqlalchemy.future import select
from sqlalchemy import func
from app.model.group_member import GroupMember
from app.configuration.database import AsyncSessionLocal


class GroupMemberRepository:
    async def find_by_user_and_group(self, user, group) -> GroupMember:
        """
        Tìm kiếm một GroupMember dựa vào User và Group.
        Giả sử user và group đều có thuộc tính `id`.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupMember).where(
                    GroupMember.user_id == user.id,
                    GroupMember.group_id == group.id
                )
            )
            return result.scalar_one_or_none()

    async def find_group_members_by_user(self, user) -> list:
        """
        Tìm danh sách GroupMember (bao gồm cả Group) mà User thuộc về.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupMember)
                .where(GroupMember.user_id == user.id)
                # Nếu cần load luôn đối tượng Group, có thể sử dụng eager loading (ví dụ: selectinload)
            )
            return result.scalars().all()

    async def find_group_members_by_group(self, group) -> list:
        """
        Tìm danh sách GroupMember (bao gồm cả User) của một Group.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupMember).where(GroupMember.group_id == group.id)
            )
            return result.scalars().all()

    async def exists_by_user_and_group(self, user, group) -> bool:
        """
        Kiểm tra xem một User có thuộc về một Group không.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count(GroupMember.id)).where(
                    GroupMember.user_id == user.id,
                    GroupMember.group_id == group.id
                )
            )
            count = result.scalar_one()
            return count > 0
