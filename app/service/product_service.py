from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_repository import ProductRepository
from app.schema.product_schema import ProductCreate

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    async def create_new_product(self, db: AsyncSession, product: ProductCreate):
        return await self.repository.create_product(db, product)

    async def fetch_product_by_id(self, db: AsyncSession, product_id: int):
        return await self.repository.get_product_by_id(db, product_id)
