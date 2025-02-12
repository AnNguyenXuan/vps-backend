from fastapi import HTTPException, status
from app.repository.category_repository import CategoryRepository
from app.schema.category_schema import CategoryCreate, CategoryUpdate
from app.model.category import Category
from app.service.product_service import ProductService
from app.core.exceptions import DuplicateDataError


class CategoryService:

    def __init__(self):
        self.repository = CategoryRepository()
        self.product_service = ProductService()

    async def get_all_categories(self):
        """Lấy tất cả danh mục"""
        return await self.repository.find_all()

    async def get_category_by_id(self, category_id: int):
        """Lấy danh mục theo ID"""
        category = await self.repository.find_by_id(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

    async def get_subcategories_by_parent_id(self, parent_id: int):
        """Lấy danh mục con theo parent_id"""
        return await self.repository.find_by_parent_id(parent_id)

    async def create_category(self, category_data: CategoryCreate):
        """Tạo danh mục mới"""
        # Nếu có parent_id, kiểm tra xem danh mục cha có tồn tại không
        if category_data.parent_id:
            parent = await self.get_category_by_id(category_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found"
                )

        # Khởi tạo đối tượng Category từ dữ liệu đầu vào
        new_category = Category(**category_data.model_dump())
        try:
            return await self.repository.create_category(new_category)
        except DuplicateDataError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def update_category(self, category_id: int, category_data: CategoryUpdate):
        """Cập nhật danh mục"""
        category = await self.get_category_by_id(category_id)
        update_data = category_data.model_dump(exclude_unset=True)

        # Nếu có cập nhật parent_id, thực hiện kiểm tra hợp lệ
        if "parent_id" in update_data:
            if update_data["parent_id"] in (None, ""):
                update_data["parent_id"] = None
            else:
                parent = await self.get_category_by_id(update_data["parent_id"])
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found"
                    )

        for key, value in update_data.items():
            setattr(category, key, value)
        return await self.repository.update_category(category)

    async def delete_category(self, category_id: int):
        """Xóa danh mục"""
        category = await self.get_category_by_id(category_id)

        # Cập nhật các danh mục con: chuyển parent_id của con thành parent_id của danh mục bị xóa
        children = await self.get_subcategories_by_parent_id(category_id)
        for child in children:
            child.parent_id = category.parent_id
            await self.repository.update_category(child)

        # Cập nhật sản phẩm thuộc danh mục: chuyển category_id của sản phẩm thành parent_id của danh mục bị xóa
        products = await self.product_service.find_products_by_category_id(category_id)
        for product in products:
            product.category_id = category.parent_id
            await self.product_service.update_product(product)

        success = await self.repository.delete_category(category)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete category")
        return {"message": "Category deleted"}
