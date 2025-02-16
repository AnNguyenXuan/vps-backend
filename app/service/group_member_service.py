from fastapi import HTTPException, status
from app.repository.group_member_repository import GroupMemberRepository
from app.model.user import User
from app.model.group_member import GroupMember
from app.core.exceptions import DuplicateDataError
from app.schema.group_member_schema import GroupMemberBase, GroupMemberCreate
from .user_service import UserService
from .group_service import GroupService



class GroupMemberService:
    def __init__(self):
        self.group_member_repository = GroupMemberRepository()
        self.user_service = UserService()
        self.group_service = GroupService()

    async def add_user_to_group(self, data: GroupMemberCreate) -> GroupMember:
        """
        Thêm User vào Group.
        Dữ liệu đầu vào phải chứa 'userId' và 'groupId'.
        """
        # Lấy thông tin user và group, nếu không tìm thấy sẽ được UserService/GroupService raise HTTPException
        user = await self.user_service.get_user_by_id(data.user_id)
        group = await self.group_service.get_group_by_id(data.group_id)
        group_member = GroupMember(user_id=user.id, group_id=group.id)
        try:
            group_member = await self.group_member_repository.add(group_member)
            return group_member
        except DuplicateDataError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def remove_user_from_group(self, data: GroupMemberBase) -> None:
        """
        Xóa thành viên khỏi Group.
        """
        user = await self.user_service.get_user_by_id(data.user_id)
        group = await self.group_service.get_group_by_id(data.group_id)
        group_member = await self.group_member_repository.find_by_user_and_group(user, group)
        if not group_member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group member not found")
        
        success = await self.group_member_repository.delete(group_member)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to remove user from group")

    async def find_groups_by_user(self, user: User) -> list:
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
