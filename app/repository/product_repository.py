from sqlalchemy.future import select
from sqlalchemy import or_
from app.model.product import Product
from app.configuration.database import AsyncSessionLocal


class ProductRepository:
    async def find_by_category_id(self, category_id: int) -> list:
        """Lấy danh sách sản phẩm theo ID danh mục"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Product).where(Product.category_id == category_id)
            )
            return result.scalars().all()

    async def find_all_paginated(self, page: int, limit: int) -> list:
        """Lấy danh sách sản phẩm không bị xóa với phân trang"""
        offset = (page - 1) * limit
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Product)
                .where(Product.is_delete == False)
                .order_by(Product.id.asc())
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()

    async def search_products_by_keywords(self, keywords: str) -> list:
        """Tìm sản phẩm theo từ khóa (trong tên hoặc mô tả)"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Product)
                .where(Product.is_delete == False)
                .where(
                    or_(
                        Product.name.ilike(f"%{keywords}%"),
                        Product.description.ilike(f"%{keywords}%")
                    )
                )
                .order_by(Product.id.asc())
            )
            return result.scalars().all()

    async def find_by_id(self, product_id: int):
        """Tìm sản phẩm theo ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Product).where(Product.id == product_id)
            )
            return result.scalar_one_or_none()

    async def find_all(self) -> list:
        """Lấy tất cả sản phẩm"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Product))
            return result.scalars().all()

    # --- Các phương thức ghi (create, update) được bổ sung ---

    async def create(self, product: Product) -> Product:
        """Tạo mới một sản phẩm trong cơ sở dữ liệu"""
        async with AsyncSessionLocal() as session:
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product

    async def update(self, product: Product) -> Product:
        """
        Cập nhật thông tin của sản phẩm.
        Ở đây, chúng ta add lại đối tượng (có thể đã được thay đổi) rồi commit và refresh.
        """
        async with AsyncSessionLocal() as session:
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product
