from typing import Union, Literal, List, Optional
from pydantic import BaseModel, Field, root_validator

class PermissionDetail(BaseModel):
    permission_id: int = Field(..., gt=0, description="ID quyền.")
    target: Union[int, Literal["all"]] = Field(
        ..., description="ID mục tiêu (nếu có): phải là số nguyên dương hoặc giá trị 'all'."
    )

class GroupPermissionsAssign(BaseModel):
    """
    Schema dùng để gán quyền cho nhóm (POST).
    """
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")
    permissions: List[PermissionDetail] = Field(
        ..., description="Danh sách quyền cần gán cho nhóm."
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": [
                    {"permission_id": 1, "target": 3},
                    {"permission_id": 3, "target": "all"}
                ]
            }
        }

class PermissionDetailUpdate(BaseModel):
    id: int = Field(..., gt=0, description="ID bản ghi GroupPermission.")
    record_enabled: Optional[bool] = Field(None, description="Cập nhật trạng thái quyền.")
    is_denied: Optional[bool] = Field(None, description="Cập nhật trạng thái từ chối quyền.")

class GroupPermissionsUpdate(BaseModel):
    """
    Schema dùng để cập nhật quyền cho nhóm (PUT).
    """
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")
    permissions: List[PermissionDetailUpdate] = Field(
        ..., description="Danh sách quyền cần cập nhật."
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": [
                    {"id": 1, "record_enabled": True},
                    {"id": 2, "is_denied": False}
                ]
            }
        }

class GroupPermissionsDelete(BaseModel):
    """
    Schema dùng để thu hồi quyền của nhóm (DELETE).
    """
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")
    permissions: List[int] = Field(
        ..., description="Danh sách ID quyền cần thu hồi."
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": [1, 2, 3]
            }
        }

class GroupPermissionsReadDetail(BaseModel):
    id: int = Field(..., description="ID của bản ghi GroupPermission")
    permission_id: int = Field(..., description="ID của quyền")
    name: str = Field(..., description="Tên quyền (lấy từ permission.name)")
    record_enabled: bool = Field(..., description="Bản ghi phân quyền này có được kích hoạt hay không")
    is_denied: bool = Field(..., description="Quyền có bị từ chối hay không")
    target: Union[int, Literal["all"]] = Field(
        ..., description="Target của quyền; nếu cột target_id là None thì trả về 'all', ngược lại trả về số tương ứng."
    )

class GroupPermissionsRead(BaseModel):
    group_id: int = Field(..., description="ID của nhóm")
    permissions: List[GroupPermissionsReadDetail] = Field(
        ..., description="Danh sách chi tiết quyền của nhóm"
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": [
                    {"id": 1, "permission_id": 1, "name": "edit_user", "target": 3},
                    {"id": 2, "permission_id": 3, "name": "create_category", "target": "all"}
                ]
            }
        }
