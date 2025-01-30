from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.user import User



class UserRepository:
    
    async def create_user(self, db: AsyncSession, new_user: User):
        """ Tạo mới người dùng """      
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def update_user(self, db: AsyncSession, user: User):
        """ Cập nhật thông tin người dùng """
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, user: User):
        """ Xóa người dùng """
        await db.delete(user)
        await db.commit()

    async def get_active_users_paginated(self, db: AsyncSession, page: int, limit: int):
        """ Lấy danh sách user đang hoạt động (is_active=True) với phân trang """
        offset = (page - 1) * limit
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
            .order_by(User.id.asc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_by_id(self, db: AsyncSession, user_id: int):
        """ Tìm user theo ID """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, db: AsyncSession, username: str):
        """ Tìm user theo username """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str):
        """ Tìm user theo email """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
