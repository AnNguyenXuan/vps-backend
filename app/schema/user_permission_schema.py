from typing import Union, Literal, List, Optional
from pydantic import BaseModel, Field

class PermissionDetail(BaseModel):
    permission_id: int = Field(..., gt=0, description="Id quyền.")
    target: Union[int, Literal["all"]] = Field(
        ...,
        description="ID mục tiêu (nếu có): phải là số nguyên dương hoặc giá trị 'all'."
    )

class UserPermissionsAssign(BaseModel):
    """
    Schema dùng để gán quyền cho người dùng (POST).
    """
    user_id: int = Field(..., gt=0, description="ID của người dùng, phải là số nguyên dương.")
    permissions: List[PermissionDetail] = Field(
        ...,
        description="Mapping giữa tên quyền và chi tiết quyền."
    )

    class Config:
        schema_extra = {
            "example": {
                "user_id": 4,
                "permissions": [
                    {"permission_id": 1, "target": 3},
                    {"permission_id": 3, "target": "all"}
                ]
            }
        }

class PermissionDetailUpdate(BaseModel):
    id: int = Field(..., gt=0, description="Id bản ghi.")
    record_enabled: Optional[bool] = Field(
        None, 
        description="Cập nhật trạng thái quyền."
    )
    is_denied: Optional[bool] = Field(
        None, 
        description="Cập nhật trạng thái từ chối quyền."
    )

class UserPermissionsUpdate(BaseModel):
    """
    Schema dùng để cập nhật quyền cho người dùng (PUT).
    """
    user_id: int = Field(..., gt=0, description="ID của người dùng, phải là số nguyên dương.")
    permissions: List[PermissionDetailUpdate] = Field(
        ...,
        description="Mapping giữa tên quyền và các trường cần cập nhật."
    )

    class Config:
        schema_extra = {
            "example": {
                "user_id": 4,
                "permissions": [
                    {"id": 1, "record_enabled": True},
                    {"id": 2, "is_denied": False}
                ]
            }
        }

class UserPermissionsDelete(BaseModel):
    """
    Schema dùng để thu hồi quyền của người dùng (DELETE).
    """
    user_id: int = Field(..., gt=0, description="ID của người dùng, phải là số nguyên dương.")
    permissions: List[int] = Field(
        ...,
        description="Danh sách tên quyền cần thu hồi."
    )

    class Config:
        schema_extra = {
            "example": {
                "user_id": 4,
                "permissions": [1, 2, 3]
            }
        }

class UserPermissionsReadDetail(BaseModel):
    id: int = Field(..., description="ID của bản ghi UserPermission")
    permission_id: int = Field(..., description="ID của quyền")
    name: str = Field(..., description="Tên quyền (lấy từ permission.name)")
    record_enabled: bool = Field(..., description="Bản ghi phân quyền này có được kích hoạt hay không")
    is_denied: bool = Field(..., description="Quyền có bị từ chối hay không")
    target: Union[int, Literal["all"]] = Field(
        ...,
        description="Target của quyền; nếu cột target_id là None thì trả về 'all', ngược lại trả về số tương ứng."
    )

class UserPermissionsRead(BaseModel):
    user_id: int = Field(..., description="ID của người dùng")
    permissions: List[UserPermissionsReadDetail] = Field(
        ...,
        description="Danh sách chi tiết quyền của người dùng"
    )

    class Config:
        schema_extra = {
            "example": {
                "user_id": 4,
                "permissions": [
                    {"id": 1, "permission_id": 1, "name": "edit_user", "target": 3},
                    {"id": 2, "permission_id": 3, "name": "create_category", "target": "all"}
                ]
            }
        }
