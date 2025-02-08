from pydantic import BaseModel, Field

class PermissionBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$", description="Tên quyền, chỉ chứa chữ cái, số và dấu gạch dưới.")
    description: str | None = Field(None, max_length=255, description="Mô tả về quyền, tối đa 255 ký tự.")

class PermissionCreate(PermissionBase):
    """
    Schema dùng để tạo mới một quyền.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "manage_users",
                "description": "Quyền quản lý người dùng."
            }
        }
    }

class PermissionUpdate(BaseModel):
    """
    Schema dùng để cập nhật quyền.
    """
    name: str | None = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$", description="Tên quyền mới, nếu cần thay đổi.")
    description: str | None = Field(None, max_length=255, description="Mô tả mới về quyền.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "edit_users",
                "description": "Cập nhật mô tả quyền quản lý người dùng."
            }
        }
    }

class PermissionRead(PermissionBase):
    """
    Schema dùng để đọc dữ liệu của quyền.
    """
    id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "manage_users",
                "description": "Quyền quản lý người dùng."
            }
        }
    }

