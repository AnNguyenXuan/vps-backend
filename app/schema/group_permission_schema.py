from typing import Union, Literal, List
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator


class PermissionDetail(BaseModel):
    permission_id: Annotated[int, Field(gt=0, description="ID quyền.")]
    target: Union[int, Literal["all"]]

    @field_validator("target")
    @classmethod
    def validate_target(cls, value):
        if isinstance(value, int) and value <= 0:
            raise ValueError("Target phải là số nguyên dương hoặc 'all'.")
        return value


class GroupPermissionsAssign(BaseModel):
    """
    Schema dùng để gán quyền cho nhóm (POST).
    """
    group_id: Annotated[int, Field(gt=0, description="ID của nhóm, phải là số nguyên dương.")]
    permissions: List[PermissionDetail]

    model_config = {
        "json_schema_extra": {
            "example": {
                "group_id": 3,
                "permissions": [
                    {"permission_id": 1, "target": 3},
                    {"permission_id": 3, "target": "all"}
                ]
            }
        }
    }


class PermissionDetailUpdate(BaseModel):
    id: Annotated[int, Field(gt=0, description="ID bản ghi GroupPermission.")]
    record_enabled: bool | None = None
    is_denied: bool | None = None


class GroupPermissionsUpdate(BaseModel):
    """
    Schema dùng để cập nhật quyền cho nhóm (PUT).
    """
    group_id: Annotated[int, Field(gt=0, description="ID của nhóm, phải là số nguyên dương.")]
    permissions: List[PermissionDetailUpdate]

    model_config = {
        "json_schema_extra": {
            "example": {
                "group_id": 3,
                "permissions": [
                    {"id": 1, "record_enabled": True},
                    {"id": 2, "is_denied": False}
                ]
            }
        }
    }


class GroupPermissionsDelete(BaseModel):
    """
    Schema dùng để thu hồi quyền của nhóm (DELETE).
    """
    group_id: Annotated[int, Field(gt=0, description="ID của nhóm, phải là số nguyên dương.")]
    permissions: List[int]

    model_config = {
        "json_schema_extra": {
            "example": {
                "group_id": 3,
                "permissions": [1, 2, 3]
            }
        }
    }


class GroupPermissionsReadDetail(BaseModel):
    id: int
    permission_id: int
    name: str
    record_enabled: bool
    is_denied: bool
    target: Union[int, Literal["all"]]


class GroupPermissionsRead(BaseModel):
    group_id: int
    permissions: List[GroupPermissionsReadDetail]

    model_config = {
        "json_schema_extra": {
            "example": {
                "group_id": 3,
                "permissions": [
                    {"id": 1, "permission_id": 1, "name": "edit_user", "target": 3},
                    {"id": 2, "permission_id": 3, "name": "create_category", "target": "all"}
                ]
            }
        }
    }
