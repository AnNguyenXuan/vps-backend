from fastapi import APIRouter, HTTPException, Request, status
from typing import List
from app.service.permission_service import PermissionService
# from app.service.authorization_service import AuthorizationService

router = APIRouter(prefix="/api/permission", tags=["Permission"])


permission_service = PermissionService()  
# authorization_service = AuthorizationService()

@router.get("", response_model=List[str])
async def list_permissions(request: Request):
    """
    Lấy danh sách tất cả các quyền.

    Yêu cầu:
      - Người dùng (user) phải tồn tại (được gán vào request.state.user).
      - Người dùng có quyền "view_permissions".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    
    # if not authorization_service.check_permission(user, "view_permissions"):
    #     raise HTTPException(status_code=403, detail="E2020")
    
    permissions = await permission_service.view_all_permissions()
    return permissions
