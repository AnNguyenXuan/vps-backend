from fastapi import HTTPException, status
from app.repository.group_member_repository import GroupMemberRepository
from app.model.group_member import GroupMember
from app.configuration.database import AsyncSessionLocal
from app.exception import AppException  # Giả sử bạn có định nghĩa ngoại lệ riêng

class GroupMemberService:
    def __init__(self, group_member_repository: GroupMemberRepository, user_service, group_service):
        self.group_member_repository = group_member_repository
        self.user_service = user_service
        self.group_service = group_service

    async def add_user_to_group(self, data: dict) -> GroupMember:
        """
        Thêm User vào Group.
        Dữ liệu đầu vào phải chứa 'userId' và 'groupId'.
        """
        user = await self.user_service.get_user_by_id(data["userId"])
        group = await self.group_service.get_group_by_id(data["groupId"])

        group_member = GroupMember(user=user, group=group)

        async with AsyncSessionLocal() as session:
            session.add(group_member)
            await session.commit()
            await session.refresh(group_member)
        return group_member

    async def remove_user_from_group(self, data: dict) -> None:
        """
        Xóa thành viên khỏi Group.
        """
        user = await self.user_service.get_user_by_id(data["userId"])
        group = await self.group_service.get_group_by_id(data["groupId"])

        group_member = await self.group_member_repository.find_by_user_and_group(user, group)
        if group_member:
            async with AsyncSessionLocal() as session:
                await session.delete(group_member)
                await session.commit()

    async def find_groups_by_user(self, user) -> list:
        """
        Tìm danh sách Group mà User thuộc về.
        Trả về danh sách đối tượng Group.
        """
        group_members = await self.group_member_repository.find_group_members_by_user(user)
        groups = [gm.group for gm in group_members]
        return groups

    async def get_groups_by_user(self, user_id: int) -> list:
        """
        Tìm danh sách Group mà User thuộc về dựa theo user ID.
        """
        user = await self.user_service.get_user_by_id(user_id)
        group_members = await self.group_member_repository.find_group_members_by_user(user)
        groups = [gm.group for gm in group_members]
        return groups

    async def get_users_in_group(self, group_id: int) -> list:
        """
        Lấy danh sách User trong một Group dựa theo group ID.
        """
        group = await self.group_service.get_group_by_id(group_id)
        group_members = await self.group_member_repository.find_group_members_by_group(group)
        users = [gm.user for gm in group_members]
        return users

    async def is_user_in_group(self, data: dict) -> bool:
        """
        Kiểm tra xem một User có thuộc về một Group không.
        Dữ liệu đầu vào phải chứa 'userId' và 'groupId'.
        """
        user = await self.user_service.get_user_by_id(data["userId"])
        group = await self.group_service.get_group_by_id(data["groupId"])
        return await self.group_member_repository.exists_by_user_and_group(user, group)
