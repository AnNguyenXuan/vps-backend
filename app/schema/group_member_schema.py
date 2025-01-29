from pydantic import BaseModel

class GroupMemberBase(BaseModel):
    user_id: int
    group_id: int

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMemberRead(GroupMemberBase):
    pass
