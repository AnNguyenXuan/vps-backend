# app/services/product.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_repository import create_product, get_product_by_id
from app.schema.product_schema import ProductCreate

async def create_new_product(db: AsyncSession, product: ProductCreate):
    return await create_product(db, product)

async def fetch_product_by_id(db: AsyncSession, product_id: int):
    return await get_product_by_id(db, product_id)
