from pydantic import BaseModel, Field, field_validator

class UserPermissionBase(BaseModel):
    user_id: int = Field(..., gt=0, description="ID của người dùng, phải là số nguyên dương.")
    permission_id: int = Field(..., gt=0, description="ID của quyền, phải là số nguyên dương.")
    target_id: int | None = Field(None, gt=0, description="ID mục tiêu (nếu có), phải là số nguyên dương hoặc None.")
    is_active: bool = Field(True, description="Quyền có hiệu lực hay không.")
    is_denied: bool = Field(False, description="Có từ chối quyền hay không.")

    @field_validator("is_denied")
    @classmethod
    def validate_is_denied(cls, value, values):
        if value and values.data.get("is_active", True):
            raise ValueError("Không thể vừa kích hoạt (is_active=True) vừa từ chối quyền (is_denied=True).")
        return value

class UserPermissionCreate(UserPermissionBase):
    """
    Schema dùng để gán quyền cho người dùng.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 5,
                "permission_id": 3,
                "target_id": 10,
                "is_active": True,
                "is_denied": False
            }
        }
    }

class UserPermissionUpdate(BaseModel):
    """
    Schema dùng để cập nhật quyền của người dùng.
    """
    is_active: bool | None = Field(None, description="Cập nhật trạng thái quyền.")
    is_denied: bool | None = Field(None, description="Cập nhật trạng thái từ chối quyền.")
    target_id: int | None = Field(None, gt=0, description="Cập nhật ID mục tiêu.")

    @field_validator("is_denied")
    @classmethod
    def validate_update_is_denied(cls, value, values):
        if value and values.data.get("is_active", True):
            raise ValueError("Không thể vừa kích hoạt (is_active=True) vừa từ chối quyền (is_denied=True).")
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_active": False,
                "is_denied": True,
                "target_id": 10
            }
        }
    }

class UserPermissionRead(UserPermissionBase):
    """
    Schema dùng để đọc dữ liệu quyền của người dùng.
    """
    id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 5,
                "permission_id": 3,
                "target_id": 10,
                "is_active": True,
                "is_denied": False
            }
        }
    }
