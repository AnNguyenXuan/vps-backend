from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.model.user import User
from app.core.database import AsyncSessionLocal
from app.core.exceptions import DuplicateDataError

class UserRepository:

    async def create_user(self, new_user: User):
        """Tạo mới người dùng với xử lý lỗi trùng dữ liệu"""
        async with AsyncSessionLocal() as session:
            try:
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
            except IntegrityError:
                await session.rollback()
                raise DuplicateDataError("Username hoặc Email đã tồn tại")

    async def update_user(self, user: User):
        """Cập nhật thông tin người dùng"""
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def delete_user(self, user: User) -> bool:
        """Xóa người dùng và trả về True nếu thành công, False nếu thất bại"""
        async with AsyncSessionLocal() as session:
            try:
                await session.delete(user)
                await session.commit()
                return True  # Xóa thành công
            except SQLAlchemyError:
                await session.rollback()  # Rollback nếu có lỗi
                return False  # Xóa thất bại

    async def get_active_users_paginated(self, page: int, limit: int):
        """Lấy danh sách user đang hoạt động (is_active=True) với phân trang"""
        offset = (page - 1) * limit
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User)
                .where(User.is_active == True)
                .order_by(User.id.asc())
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Tìm user theo ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Tìm user theo username"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Tìm user theo email"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
