from pydantic import BaseModel, field_validator, StringConstraints
from typing_extensions import Annotated

class GroupBase(BaseModel):
    name: Annotated[
        str, 
        StringConstraints(
            min_length=1, 
            max_length=100, 
            strip_whitespace=True, 
            pattern=r"^[a-zA-Z0-9\s\-_&]+$"
        )
    ]
    description: Annotated[str, StringConstraints(max_length=500)] | None = None

class GroupCreate(GroupBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Quản trị viên",
                "description": "Nhóm người dùng có quyền quản trị hệ thống."
            }
        }
    }

class GroupRead(GroupBase):
    id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Quản trị viên",
                "description": "Nhóm người dùng có quyền quản trị hệ thống."
            }
        }
    }

