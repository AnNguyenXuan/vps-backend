# app/services/category.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.category_repository import create_category, get_category_by_id
from app.schema.category_schema import CategoryCreate

async def create_new_category(db: AsyncSession, category: CategoryCreate):
    return await create_category(db, category)

async def fetch_category_by_id(db: AsyncSession, category_id: int):
    return await get_category_by_id(db, category_id)
