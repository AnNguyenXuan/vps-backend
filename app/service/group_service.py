from fastapi import HTTPException, status
from app.repository.group_repository import GroupRepository
from app.schema.group_schema import GroupCreate, GroupUpdate
from app.model.group import Group
from app.core.exceptions import DuplicateDataError

class GroupService:
    def __init__(self):
        self.repository = GroupRepository()

    async def get_paginated_groups(self, page: int, limit: int):
        """Lấy danh sách nhóm theo phân trang"""
        return await self.repository.get_groups_paginated(page, limit)

    async def get_group_by_id(self, group_id: int):
        """Lấy thông tin nhóm theo ID"""
        group = await self.repository.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group

    async def create_group(self, new_group: GroupCreate):
        """Tạo nhóm mới"""
        group = Group(**new_group.model_dump())
        try:
            return await self.repository.create_group(group)
        except DuplicateDataError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def update_group(self, group_id: int, data: GroupUpdate):
        """Cập nhật thông tin nhóm"""
        group = await self.get_group_by_id(group_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(group, key, value)
        return await self.repository.update_group(group)

    async def delete_group(self, group_id: int):
        """Xóa nhóm"""
        group = await self.get_group_by_id(group_id)
        success = await self.repository.delete_group(group)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete group")
        return {"message": "Group deleted"}
