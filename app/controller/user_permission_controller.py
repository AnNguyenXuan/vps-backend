from fastapi import APIRouter, HTTPException, Request, status
from app.service.user_permission_service import UserPermissionService
from app.service.user_service import UserService
# from app.service.authorization_service import AuthorizationService
# from app.exception import AppException  # Giả sử bạn đã định nghĩa exception riêng

router = APIRouter(prefix="/api/user-permissions", tags=["UserPermission"])

user_permission_service = UserPermissionService()
user_service = UserService()  # Hoặc instance được khởi tạo theo cách của bạn
# authorization_service = AuthorizationService()
# Nếu có validator, bạn có thể khởi tạo và sử dụng tương tự.

@router.post("", status_code=status.HTTP_201_CREATED)
async def assign_permission(request: Request):
    """
    Gán (assign) quyền cho người dùng.
    
    Yêu cầu:
      - Thông tin user phải có trong `request.state.user`.
      - User hiện tại phải có quyền "create_permission".
      - Payload JSON phải chứa các trường cần thiết, ví dụ:
      
            {
                "user_id": 123,
                "permissions": {
                    "permission_name_1": {"target": "all", "is_active": true, "is_denied": false},
                    "permission_name_2": {"target": 456, "is_active": true, "is_denied": true}
                }
            }
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "create_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    try:
        assigned_permissions = await user_permission_service.assign_permissions(data)
        return assigned_permissions
    # except AppException as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/{userId}")
async def get_permissions_by_user(userId: int, request: Request):
    """
    Lấy danh sách tên quyền của người dùng theo userId.
    
    Yêu cầu:
      - Thông tin user phải có trong `request.state.user`.
      - User hiện tại phải có quyền "view_permissions".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_permissions"):
    #     raise HTTPException(status_code=403, detail="E2021")
    # try:
    target_user = await user_service.get_user_by_id(userId)
    user_permissions = await user_permission_service.get_permissions_by_user(target_user)
    return user_permissions
    # except AppException as e:
    #     raise HTTPException(status_code=400, detail=str(e))

@router.put("")
async def update_permission(request: Request):
    """
    Cập nhật quyền của người dùng.
    
    Yêu cầu:
      - Thông tin user phải có trong `request.state.user`.
      - User hiện tại phải có quyền "edit_permission".
      - Payload JSON phải chứa: user_id và permissions (cấu trúc tương tự như bên assign).
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "edit_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    try:
        updated_permissions = await user_permission_service.update_permission(data)
        return updated_permissions
    # except AppException as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.post("/check")
async def has_permission(request: Request):
    """
    Kiểm tra quyền của người dùng.
    
    Yêu cầu:
      - Thông tin user phải có trong `request.state.user`.
      - User hiện tại phải có quyền "view_permissions".
      - Payload JSON phải chứa: user_id, permission_name, và tùy chọn target_id.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_permissions"):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    user_id = data.get("user_id")
    permission_name = data.get("permission_name")
    target_id = data.get("target_id")
    if not user_id or not permission_name:
        raise HTTPException(status_code=400, detail="Invalid input.")
    
    try:
        has_perm = await user_permission_service.has_permission(user_id, permission_name, target_id)
        return {"has_permission": has_perm}
    # except AppException as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.delete("")
async def delete_permission(request: Request):
    """
    Xóa quyền của người dùng.
    
    Yêu cầu:
      - Thông tin user phải có trong `request.state.user`.
      - User hiện tại phải có quyền "delete_permission".
      - Payload JSON phải chứa: user_id và danh sách permission names cần xóa, ví dụ:
      
            {
                "user_id": 123,
                "permissions": ["permission_name_1", "permission_name_2"]
            }
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "delete_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # try:
    await user_permission_service.delete_permissions(data)
    return {"message": "Permissions deleted successfully."}
    # except AppException as e:
    #     raise HTTPException(status_code=400, detail=str(e))
