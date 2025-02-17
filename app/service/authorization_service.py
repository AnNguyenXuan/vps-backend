from typing import Optional, List
from app.model.user import User
from .user_permission_service import UserPermissionService
from .group_member_service import GroupMemberService
from .group_permission_service import GroupPermissionService
from .permission_service import PermissionService

class AuthorizationService:
    def __init__(self):
        self.user_permission_service = UserPermissionService()
        self.group_member_service = GroupMemberService()
        self.group_permission_service = GroupPermissionService()
        self.permission_service = PermissionService()

    async def check_permission(
        self,
        user: User,
        permission_name: str,
        target_id: Optional[int] = None,
        is_user_owned: bool = False
    ) -> bool:
        """
        Kiểm tra quyền của người dùng hoặc nhóm.

        :param user: Đối tượng người dùng cần kiểm tra
        :param permission_name: Tên quyền cần kiểm tra
        :param target_id: (Tùy chọn) ID của đối tượng đích cần kiểm tra quyền
        :param is_user_owned: Tài nguyên truy cập, chỉnh sửa thuộc về người đang đăng nhập, và user_permission_service không có phản hồi rõ ràng rằng người dùng có quyền hay không.
        :return: True nếu người dùng hoặc nhóm có quyền, False nếu không
        """
        # 1. Kiểm tra quyền của người dùng
        user_permission = await self.user_permission_service.has_permission(user.id, permission_name, target_id)
        if user_permission < 0:
            return False
        elif user_permission > 0:
            return True

        if is_user_owned:
            return True

        # 2. Lấy danh sách các nhóm mà người dùng thuộc về
        groups = await self.group_member_service.find_groups_by_user(user)

        # 3. Kiểm tra quyền của từng nhóm
        for group in groups:
            if await self.group_permission_service.has_permission(group.id, permission_name, target_id)>0:
                return True

        # 4. Nếu không tìm thấy quyền hợp lệ, kiểm tra mặc định từ permission
        permission = await self.permission_service.get_permission_by_name(permission_name)
        if permission:
            return permission.default
        else:
            return False
