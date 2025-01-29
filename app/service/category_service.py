from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.category_repository import CategoryRepository
from app.schema.category_schema import CategoryCreate

class CategoryService:
    def __init__(self):
        self.repository = CategoryRepository()

    async def create_new_category(self, db: AsyncSession, category: CategoryCreate):
        return await self.repository.create_category(db, category)

    async def fetch_category_by_id(self, db: AsyncSession, category_id: int):
        return await self.repository.get_category_by_id(db, category_id)
