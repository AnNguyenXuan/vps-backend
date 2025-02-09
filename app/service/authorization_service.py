# app/service/authorization_service.py

from typing import Optional, Any, List

class AuthorizationService:
    def __init__(
        self,
        user_permission_service: Any,
        group_member_service: Any,
        group_permission_service: Any,
        permission_service: Any
    ):
        """
        Khởi tạo AuthorizationService với các service phụ thuộc:
         - user_permission_service: Service kiểm tra quyền của người dùng.
         - group_member_service: Service lấy danh sách nhóm mà người dùng thuộc về.
         - group_permission_service: Service kiểm tra quyền của nhóm.
         - permission_service: Service lấy thông tin quyền theo tên.
        """
        self.user_permission_service = user_permission_service
        self.group_member_service = group_member_service
        self.group_permission_service = group_permission_service
        self.permission_service = permission_service

    def check_permission(
        self,
        user: Any,
        permission_name: str,
        target_id: Optional[int] = None,
        is_user_owned: bool = False
    ) -> bool:
        """
        Kiểm tra quyền của người dùng hoặc nhóm.

        :param user: Đối tượng người dùng cần kiểm tra (giả sử có thuộc tính 'id')
        :param permission_name: Tên quyền cần kiểm tra
        :param target_id: (Tùy chọn) ID của đối tượng đích cần kiểm tra quyền
        :param is_user_owned: Nếu True, trả về True sau khi không có phản hồi rõ ràng từ userPermission
        :return: True nếu người dùng hoặc nhóm có quyền, False nếu không
        """
        # 1. Kiểm tra quyền của người dùng
        user_permission = self.user_permission_service.has_permission(user.id, permission_name, target_id)
        if user_permission < 0:
            return False
        elif user_permission > 0:
            return True

        if is_user_owned:
            return True

        # 2. Lấy danh sách các nhóm mà người dùng thuộc về
        groups: List[Any] = self.group_member_service.find_groups_by_user(user)

        # 3. Kiểm tra quyền của từng nhóm
        for group in groups:
            if self.group_permission_service.has_permission(group, permission_name, target_id):
                return True

        # 4. Nếu không tìm thấy quyền hợp lệ, kiểm tra mặc định từ permission
        permission = self.permission_service.get_permission_by_name(permission_name)
        if permission:
            return permission.get_default()
        else:
            return False
