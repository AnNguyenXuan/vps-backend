from fastapi import APIRouter, HTTPException
from typing import List
from app.service.permission_service import PermissionService
from app.core.security import user_context, authorization



router = APIRouter(prefix="/permission", tags=["Permission"])

permission_service = PermissionService()  

@router.get("", response_model=List[str])
async def list_permissions():
    """
    Lấy danh sách tất cả các quyền.

    Yêu cầu:
      - Người dùng cần đăng nhập.
      - Người dùng có quyền "view_permissions".
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "view_permissions"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")
    
    permissions = await permission_service.view_all_permissions()
    return permissions
