from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.model.category import Category
from app.core.database import AsyncSessionLocal
from app.core.exceptions import DuplicateDataError


class CategoryRepository:

    async def find_by_parent_id(self, parent_id: int):
        """Tìm danh mục con theo parent_id"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Category).where(Category.parent_id == parent_id)
            )
            return result.scalars().all()

    async def find_by_id(self, category_id: int):
        """Tìm danh mục theo ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Category).where(Category.id == category_id))
            return result.scalar_one_or_none()

    async def find_all(self):
        """Lấy tất cả danh mục"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Category))
            return result.scalars().all()

    async def create_category(self, category: Category):
        """Tạo danh mục mới với xử lý lỗi trùng dữ liệu"""
        async with AsyncSessionLocal() as session:
            try:
                session.add(category)
                await session.commit()
                await session.refresh(category)
                return category
            except IntegrityError:
                await session.rollback()
                raise DuplicateDataError("Category name already exists")

    async def update_category(self, category: Category):
        """Cập nhật danh mục"""
        async with AsyncSessionLocal() as session:
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category

    async def delete_category(self, category: Category) -> bool:
        """Xóa danh mục và trả về True nếu thành công, False nếu thất bại"""
        async with AsyncSessionLocal() as session:
            try:
                await session.delete(category)
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                return False
