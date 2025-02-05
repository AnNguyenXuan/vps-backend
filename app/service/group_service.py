from fastapi import HTTPException, status
from app.repository.group_repository import GroupRepository

class GroupService:
    def __init__(self):
        self.repository = GroupRepository()

    async def get_paginated_groups(self, page: int, limit: int):
        """ Lấy danh sách nhóm theo phân trang """
        return await self.repository.get_groups_paginated(page, limit)

    async def get_group_by_id(self, group_id: int):
        """ Lấy thông tin nhóm theo ID """
        group = await self.repository.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group

    async def create_group(self, data: dict):
        """ Tạo nhóm mới """
        if not data.get("name"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
        
        existing_group = await self.repository.get_group_by_name(data["name"])
        if existing_group:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group name already exists")
        
        return await self.repository.create_group(data)

    async def update_group(self, group_id: int, data: dict):
        """ Cập nhật thông tin nhóm """
        updated_group = await self.repository.update_group(group_id, data)
        if not updated_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return updated_group

    async def delete_group(self, group_id: int):
        """ Xóa nhóm """
        success = await self.repository.delete_group(group_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return {"message": "Group deleted"}
