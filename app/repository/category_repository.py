from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.category import Category
from app.schema.category_schema import CategoryCreate

class CategoryRepository:
    async def create_category(self, db: AsyncSession, category: CategoryCreate):
        new_category = Category(**category.dict())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category

    async def get_category_by_id(self, db: AsyncSession, category_id: int):
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()
