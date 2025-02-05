from fastapi import HTTPException, status
from app.repository.category_repository import CategoryRepository
from app.schema.category_schema import CategoryCreate, CategoryUpdate
from app.model.category import Category
from app.service.product_service import ProductService


class CategoryService:

    def __init__(self):
        self.repository = CategoryRepository()
        self.product_service = ProductService()

    async def get_all_categories(self):
        """ Lấy tất cả danh mục """
        return await self.repository.find_all()

    async def get_category_by_id(self, category_id: int):
        """ Lấy danh mục theo ID """
        category = await self.repository.find_by_id(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

    async def get_subcategories_by_parent_id(self, parent_id: int):
        """ Lấy danh mục con theo parent_id """
        return await self.repository.find_by_parent_id(parent_id)

    async def create_category(self, category_data: CategoryCreate):
        """ Tạo danh mục mới """
        new_category = Category(
            name=category_data.name,
            description=category_data.description,
            parent_id=category_data.parent_id
        )

        if category_data.parent_id:
            parent = await self.get_category_by_id(category_data.parent_id)
            if not parent:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")

        return await self.repository.create_category(new_category)

    async def update_category(self, category_id: int, category_data: CategoryUpdate):
        """ Cập nhật danh mục """
        category = await self.get_category_by_id(category_id)

        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description
        if category_data.parent_id is not None:
            if category_data.parent_id == "":
                category.parent_id = None
            else:
                parent = await self.get_category_by_id(category_data.parent_id)
                if not parent:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")
                category.parent_id = category_data.parent_id

        return await self.repository.update_category(category)

    async def delete_category(self, category_id: int):
        """ Xóa danh mục """
        category = await self.get_category_by_id(category_id)

        # Cập nhật danh mục con
        children = await self.get_subcategories_by_parent_id(category_id)
        for child in children:
            child.parent_id = category.parent_id
            await self.repository.update_category(child)

        # Cập nhật sản phẩm thuộc danh mục
        products = await self.product_service.find_products_by_category_id(category_id)
        for product in products:
            product.category_id = category.parent_id
            await self.product_service.update_product(product)

        await self.repository.delete_category(category)
