from pydantic import BaseModel, Field

class GroupMemberBase(BaseModel):
    user_id: int = Field(..., gt=0, description="ID của người dùng, phải là số nguyên dương.")
    group_id: int = Field(..., gt=0, description="ID của nhóm, phải là số nguyên dương.")

class GroupMemberCreate(GroupMemberBase):
    """
    Schema dùng để tạo mới một GroupMember.
    """
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 10,
                "group_id": 2
            }
        }
    }


class GroupMemberRead(GroupMemberBase):
    """
    Schema dùng để đọc dữ liệu của GroupMember.
    """
    id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 10,
                "group_id": 2
            }
        }
    }

