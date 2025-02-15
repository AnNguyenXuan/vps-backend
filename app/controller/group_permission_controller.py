from fastapi import APIRouter, HTTPException, Request, status
from app.service.group_permission_service import GroupPermissionService
from app.service.group_service import GroupService
# from app.service.authorization_service import AuthorizationService
# Nếu có, import validator
# from app.validators.group_permission_validator import GroupPermissionValidator

router = APIRouter(prefix="/group-permissions", tags=["GroupPermission"])


group_service = GroupService()
group_permission_service = GroupPermissionService()
# authorization_service = AuthorizationService()
# Nếu cần dùng validator, khởi tạo như sau:
# group_permission_validator = GroupPermissionValidator()


@router.post("", status_code=status.HTTP_201_CREATED)
async def assign_permission(request: Request):
    """
    Gán (assign) danh sách quyền cho Group.
    Yêu cầu:
      - Người dùng (user) phải tồn tại (được gán vào request.state.user).
      - Có quyền "create_permission".
      - Dữ liệu JSON chứa các trường cần thiết, ví dụ:
            {
                "group_id": 123,
                "permissions": {
                    "permission_name_1": {"target": "all", "is_active": true, "is_denied": false},
                    "permission_name_2": {"target": 456, "is_active": true, "is_denied": true}
                }
            }
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E1004")
    # if not authorization_service.check_permission(user, "create_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Nếu sử dụng validator, bạn có thể kiểm tra dữ liệu:
    # validated_data = group_permission_validator.validate_assign_or_update_permission(data)
    # Ở đây, dùng data trực tiếp
    assigned_permissions = await group_permission_service.assign_permissions(data)
    return assigned_permissions


@router.get("/{groupId}")
async def get_permissions_by_group(groupId: int, request: Request):
    """
    Lấy danh sách quyền (tên quyền) của Group.
    Yêu cầu:
      - User tồn tại.
      - Có quyền "view_permissions".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E1004")
    # if not authorization_service.check_permission(user, "view_permissions"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        # Lấy thông tin group qua GroupService
        group = await group_service.get_group_by_id(groupId)
        group_permissions = await group_permission_service.get_permissions_by_group(group)
        return group_permissions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("")
async def update_permission(request: Request):
    """
    Cập nhật thông tin quyền của Group.
    Yêu cầu:
      - User tồn tại.
      - Có quyền "edit_permission".
      - Dữ liệu JSON chứa các trường cập nhật, ví dụ:
            {
                "group_id": 123,
                "permissions": {
                    "permission_name_1": {"target": "all", "is_active": true, "is_denied": false},
                    "permission_name_2": {"target": 456, "is_active": false, "is_denied": true}
                }
            }
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E1004")
    # if not authorization_service.check_permission(user, "edit_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Nếu có validator: validated_data = group_permission_validator.validate_assign_or_update_permission(data)
    updated_permissions = await group_permission_service.update_permission(data)
    return updated_permissions


@router.delete("")
async def delete_permission(request: Request):
    """
    Xóa danh sách quyền của Group.
    Yêu cầu:
      - User tồn tại.
      - Có quyền "delete_permission".
      - Dữ liệu JSON chứa:
            {
                "group_id": 123,
                "permissions": ["permission_name_1", "permission_name_2"]
            }
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E1004")
    # if not authorization_service.check_permission(user, "delete_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Nếu có validator: validated_data = group_permission_validator.validate_delete_permission(data)
    try:
        await group_permission_service.delete_permissions(data)
        return {"message": "Permissions deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
