from fastapi import APIRouter
from typing import List
from app.service.permission_service import PermissionService
# from app.service.authorization_service import AuthorizationService

router = APIRouter(prefix="/api/permission", tags=["Permission"])


permission_service = PermissionService()  
# authorization_service = AuthorizationService()

@router.get("", response_model=List[str])
async def list_permissions():
    """
    Lấy danh sách tất cả các quyền.

    Yêu cầu:
      - Người dùng (user) phải tồn tại (được gán vào request.state.user).
      - Người dùng có quyền "view_permissions".
    """

    # if not authorization_service.check_permission(user, "view_permissions"):
    #     raise HTTPException(status_code=403, detail="E2020")
    
    permissions = await permission_service.view_all_permissions()
    return permissions
