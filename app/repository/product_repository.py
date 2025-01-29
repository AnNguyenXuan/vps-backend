from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.product import Product
from app.schema.product_schema import ProductCreate

class ProductRepository:
    async def create_product(self, db: AsyncSession, product: ProductCreate):
        new_product = Product(**product.dict())
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product

    async def get_product_by_id(self, db: AsyncSession, product_id: int):
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
