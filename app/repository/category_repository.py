from sqlalchemy.future import select
from app.model.category import Category
from app.configuration.database import AsyncSessionLocal


class CategoryRepository:

    async def find_by_parent_id(self, parent_id: int):
        """ Tìm danh mục con theo parent_id """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Category).where(Category.parent_id == parent_id)
            )
            return result.scalars().all()

    async def find_by_id(self, category_id: int):
        """ Tìm danh mục theo ID """
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Category).where(Category.id == category_id))
            return result.scalar_one_or_none()

    async def find_all(self):
        """ Lấy tất cả danh mục """
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Category))
            return result.scalars().all()

    async def create_category(self, category: Category):
        """ Tạo danh mục mới """
        async with AsyncSessionLocal() as session:
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category

    async def update_category(self, category: Category):
        """ Cập nhật danh mục """
        async with AsyncSessionLocal() as session:
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category

    async def delete_category(self, category: Category):
        """ Xóa danh mục """
        async with AsyncSessionLocal() as session:
            await session.delete(category)
            await session.commit()
