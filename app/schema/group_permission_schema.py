from typing import Union, Literal, Dict, List, Optional
from pydantic import BaseModel, Field, root_validator

class GroupPermissionDetail(BaseModel):
    record_enabled: bool = Field(..., description="Quyền có hiệu lực hay không.")
    is_denied: bool = Field(..., description="Có từ chối quyền hay không.")
    target: Union[int, Literal["all"]] = Field(
        ...,
        description="ID mục tiêu (nếu có): phải là số nguyên dương hoặc giá trị 'all'."
    )

    @root_validator
    def check_active_denied(cls, values):
        record_enabled = values.get("record_enabled")
        is_denied = values.get("is_denied")
        if record_enabled and is_denied:
            raise ValueError("Không thể vừa kích hoạt (record_enabled=True) vừa từ chối quyền (is_denied=True).")
        return values

class GroupPermissionsAssign(BaseModel):
    """
    Schema dùng để gán quyền cho nhóm (POST).
    """
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")
    permissions: Dict[str, GroupPermissionDetail] = Field(
        ...,
        description="Mapping giữa tên quyền và chi tiết quyền."
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": {
                    "edit_user": {"record_enabled": True, "is_denied": False, "target": 3},
                    "create_category": {"record_enabled": False, "is_denied": False, "target": 3},
                    "edit_product": {"record_enabled": True, "is_denied": False, "target": "all"}
                }
            }
        }

class GroupPermissionDetailUpdate(BaseModel):
    record_enabled: Optional[bool] = Field(None, description="Cập nhật trạng thái quyền.")
    is_denied: Optional[bool] = Field(None, description="Cập nhật trạng thái từ chối quyền.")
    target: Optional[Union[int, Literal["all"]]] = Field(
        None,
        description="Cập nhật ID mục tiêu hoặc giá trị 'all'."
    )

    @root_validator
    def check_active_denied(cls, values):
        record_enabled = values.get("record_enabled")
        is_denied = values.get("is_denied")
        if record_enabled is True and is_denied is True:
            raise ValueError("Không thể vừa kích hoạt (record_enabled=True) vừa từ chối quyền (is_denied=True).")
        return values

    class Config:
        schema_extra = {
            "example": {
                "record_enabled": True,
                "is_denied": False,
                "target": 3
            }
        }

class GroupPermissionsUpdate(BaseModel):
    """
    Schema dùng để cập nhật quyền cho nhóm (PUT).
    """
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")
    permissions: Dict[str, GroupPermissionDetailUpdate] = Field(
        ...,
        description="Mapping giữa tên quyền và các trường cần cập nhật."
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": {
                    "edit_user": {"record_enabled": True, "is_denied": False, "target": 3},
                    "create_category": {"record_enabled": False, "is_denied": False, "target": 3},
                    "edit_product": {"record_enabled": False, "is_denied": True, "target": "all"}
                }
            }
        }

class GroupPermissionsDelete(BaseModel):
    """
    Schema dùng để thu hồi quyền của nhóm (DELETE).
    """
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")
    permissions: List[str] = Field(
        ...,
        description="Danh sách tên quyền cần thu hồi."
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 3,
                "permissions": ["edit_user", "create_category", "edit_product"]
            }
        }
