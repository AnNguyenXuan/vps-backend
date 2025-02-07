import json
from fastapi import HTTPException, status
from app.repository.product_repository import ProductRepository
from app.repository.category_repository import CategoryRepository
from app.model.product import Product
from app.model.product_option import ProductOption
from .product_attribute_service import ProductAttributeService
from .product_attribute_value_service import ProductAttributeValueService
from .product_option_service import ProductOptionService
from .product_option_value_service import ProductOptionValueService
# from app.exception import AppException



class ProductService:
    def __init__(self):
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.product_attribute_service = ProductAttributeService()
        self.product_attribute_value_service = ProductAttributeValueService()
        self.product_option_service = ProductOptionService()
        self.product_option_value_service = ProductOptionValueService()

    async def to_dto(self, product: Product) -> dict:
        """Chuyển đối tượng Product thành dict (DTO)"""
        attributes = await self.get_product_attributes(product)
        price_and_stock = await self.get_product_price_and_stock(product)
        return {
            "id": product.id,
            "name": product.name,
            "location_address": product.location_address,
            "category_id": product.category.id if product.category else None,
            "description": product.description,
            "price": price_and_stock["prices"],
            "stock": price_and_stock["stock"],
            "attribute": attributes,
            "discount_percentage": product.discount_percentage,
        }

    async def search_products_by_keywords(self, keywords: str) -> list:
        """Tìm sản phẩm theo từ khóa và trả về DTO của sản phẩm chưa bị xóa"""
        products = await self.product_repository.search_products_by_keywords(keywords)
        result = []
        for product in products:
            if not product.is_delete:
                result.append(await self.to_dto(product))
        return result

    async def get_all_product_dtos(self) -> list:
        """Lấy tất cả sản phẩm (DTO) chưa bị xóa"""
        products = await self.product_repository.find_all()
        result = []
        for product in products:
            if not product.is_delete:
                result.append(await self.to_dto(product))
        return result

    async def get_paginated_product_dtos(self, page: int, limit: int) -> list:
        """Lấy sản phẩm theo phân trang và trả về DTO"""
        products = await self.product_repository.find_all_paginated(page, limit)
        result = []
        for product in products:
            result.append(await self.to_dto(product))
        return result

    async def get_product_dto_by_id(self, product_id: int) -> dict:
        """Lấy DTO của sản phẩm theo ID"""
        product = await self.get_product_by_id(product_id)
        return await self.to_dto(product)

    async def get_product_by_id(self, product_id: int) -> Product:
        """Tìm sản phẩm theo ID và kiểm tra xem sản phẩm có bị đánh dấu xóa không"""
        product = await self.product_repository.find_by_id(product_id)
        # if not product or product.is_delete:
        #     raise AppException("Product not found")
        return product

    async def get_product_attributes(self, product: Product) -> dict:
        """Lấy thuộc tính và giá trị của sản phẩm"""
        attributes = await self.product_attribute_service.find_by_product(product)
        result = {}
        for attr in attributes:
            values = await self.product_attribute_value_service.find_by_attribute(attr)
            result[attr.name] = [val.value for val in values]
        return result

    async def create_product(self, data: dict) -> dict:
        """Tạo sản phẩm mới"""
        # if "name" not in data:
        #     raise AppException("Name is required")
        # if "location_address" not in data:
        #     raise AppException("Location address is required")
        
        product = Product(
            name=data["name"],
            location_address=data["location_address"],
            description=data.get("description"),
            discount_percentage=data.get("discount_percentage"),
        )

        if "category_id" in data and data["category_id"]:
            category = await self.category_repository.find_by_id(data["category_id"])
            # if not category:
            #     raise AppException("Invalid category ID")
            product.category = category

        # Tạo sản phẩm trong DB thông qua repository
        product = await self.product_repository.create(product)

        # Xử lý attributes nếu có
        if "attribute" in data and isinstance(data["attribute"], dict):
            for attr_name, values in data["attribute"].items():
                product_attribute = await self.product_attribute_service.create_product_attribute(product, attr_name)
                for value in values:
                    await self.product_attribute_value_service.create_product_attribute_value(product_attribute, value)

        price = data.get("price", None)
        stock = data.get("stock", 0)
        await self.product_option_service.create_product_option(product, price, stock)

        return await self.to_dto(product)

    async def update_product(self, product_id: int, data: dict) -> dict:
        """Cập nhật thông tin sản phẩm"""
        product = await self.get_product_by_id(product_id)
        option_default = await self.find_option_default(product)
        
        if "name" in data and data["name"]:
            product.name = data["name"]
        if "location_address" in data and data["location_address"]:
            product.location_address = data["location_address"]
        if "description" in data:
            product.description = data["description"]
        if "discount_percentage" in data:
            product.discount_percentage = data["discount_percentage"]

        if "price" in data and option_default:
            option_default.price = data["price"]
        if "stock" in data and option_default:
            option_default.stock = data["stock"]

        if "category_id" in data and data["category_id"]:
            category = await self.category_repository.find_by_id(data["category_id"])
            # if not category:
            #     raise AppException("Invalid category ID")
            product.category = category

        # Cập nhật thông tin sản phẩm trong DB thông qua repository
        product = await self.product_repository.update(product)

        # Xử lý attributes nếu có
        if "attribute" in data and isinstance(data["attribute"], dict):
            for attr_name, values in data["attribute"].items():
                product_attribute = await self.product_attribute_service.find_by_name_and_product(attr_name, product)
                if not product_attribute:
                    product_attribute = await self.product_attribute_service.create_product_attribute(product, attr_name)
                current_values = await self.product_attribute_value_service.find_by_attribute(product_attribute)
                # Xóa các giá trị hiện có không có trong danh sách mới
                for current_value in current_values:
                    if current_value.value not in values:
                        # Giả sử product_attribute_value_service có hàm delete để xử lý việc xóa
                        await self.product_attribute_value_service.delete_product_attribute_value(current_value)
                # Thêm giá trị mới nếu chưa có
                for value in values:
                    existing_value = await self.product_attribute_value_service.find_by_value_and_attribute(value, product_attribute)
                    if not existing_value:
                        await self.product_attribute_value_service.create_product_attribute_value(product_attribute, value)

        return await self.to_dto(product)

    async def delete_product(self, product_id: int) -> None:
        """Đánh dấu sản phẩm là đã xóa (soft-delete)"""
        product = await self.get_product_by_id(product_id)
        product.is_delete = True
        await self.product_repository.update(product)

    async def get_product_price_and_stock(self, product: Product) -> dict:
        """Tính toán giá thấp nhất và tổng số tồn kho từ các tùy chọn sản phẩm"""
        options = await self.product_option_service.find_by_product(product)
        if len(options) == 1:
            return {"prices": options[0].price, "stock": options[0].stock}
        
        # Lọc các option có option values hợp lệ
        valid_options = []
        for option in options:
            option_values = await self.product_option_value_service.find_by_option(option)
            if option_values:
                valid_options.append(option)
        if valid_options:
            prices = [opt.price for opt in valid_options]
            total_stock = sum(opt.stock for opt in valid_options)
            return {"prices": min(prices), "stock": total_stock}
        return {"prices": None, "stock": 0}

    async def find_option_default(self, product: Product) -> ProductOption:
        """Tìm tùy chọn mặc định của sản phẩm"""
        options = await self.product_option_service.find_by_product(product)
        if len(options) == 1:
            return options[0]
        for option in options:
            option_values = await self.product_option_value_service.find_by_option(option)
            if not option_values:
                return option
        return None

    async def find_option_by_attribute_values(self, product: Product, attribute_values: list) -> ProductOption:
        """Tìm tùy chọn dựa trên danh sách các giá trị thuộc tính cho trước"""
        options = await self.product_option_service.find_by_product(product)
        for option in options:
            option_values = await self.product_option_value_service.find_by_option(option)
            option_value_ids = [val.product_attribute_value.id for val in option_values]
            attribute_value_ids = [val.id for val in attribute_values]
            if set(option_value_ids) == set(attribute_value_ids):
                return option
        return None

    async def update_or_create_product_attributes_and_options(self, product_id: int, json_data: dict) -> None:
        """Cập nhật hoặc tạo mới các thuộc tính và tùy chọn cho sản phẩm"""
        product = await self.get_product_by_id(product_id)
        # if not product:
        #     raise AppException("Product not found")

        attributes = json_data.get("attribute", [])
        values = json_data.get("value", [])

        if not attributes or not values:
            raise ValueError("Invalid input data: 'attribute' and 'value' are required.")

        # Bước 1: Đảm bảo các ProductAttribute tồn tại
        attribute_entities = []
        for attr_name in attributes:
            attribute = await self.product_attribute_service.find_by_name_and_product(attr_name, product)
            if not attribute:
                attribute = await self.product_attribute_service.create_product_attribute(product, attr_name)
            attribute_entities.append(attribute)

        # Bước 2: Xử lý các giá trị thuộc tính và tùy chọn
        for value_set in values:
            attribute_values = value_set[0] if len(value_set) > 0 else []
            option_data = value_set[1] if len(value_set) > 1 else []
            price = option_data[0] if len(option_data) > 0 else None
            stock = option_data[1] if len(option_data) > 1 else None

            if len(attribute_values) != len(attributes) or price is None or stock is None:
                raise ValueError("Invalid value set: Mismatch between attributes and values or missing price/stock.")

            attribute_value_entities = []
            for index, value in enumerate(attribute_values):
                attribute = attribute_entities[index]
                attribute_value = await self.product_attribute_value_service.find_by_value_and_attribute(value, attribute)
                if not attribute_value:
                    attribute_value = await self.product_attribute_value_service.create_product_attribute_value(attribute, value)
                else:
                    await self.product_attribute_value_service.update_product_attribute_value(attribute_value, value)
                attribute_value_entities.append(attribute_value)

            # Bước 3: Tìm hoặc tạo ProductOption
            existing_option = await self.find_option_by_attribute_values(product, attribute_value_entities)
            if not existing_option:
                product_option = await self.product_option_service.create_product_option(product, price, stock)
            else:
                await self.product_option_service.update_product_option(existing_option, price, stock)
                product_option = existing_option

            # Bước 4: Liên kết ProductOption với các giá trị thuộc tính
            for attribute_value_entity in attribute_value_entities:
                existing_option_value = await self.product_option_value_service.find_by_value_and_option(attribute_value_entity, product_option)
                if not existing_option_value:
                    await self.product_option_value_service.create_product_option_value(product_option, attribute_value_entity)

    async def find_product_option_by_json(self, product: Product, json_string: str) -> ProductOption:
        """Tìm tùy chọn sản phẩm dựa trên chuỗi JSON mô tả các thuộc tính"""
        try:
            attribute_data = json.loads(json_string)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")

        attribute_value_entities = []
        for attribute_name, attribute_value in attribute_data.items():
            product_attribute = await self.product_attribute_service.find_by_name_and_product(attribute_name, product)
            if not product_attribute:
                raise Exception(f"Attribute '{attribute_name}' not found for this product.")
            product_attribute_value = await self.product_attribute_value_service.find_by_value_and_attribute(attribute_value, product_attribute)
            if not product_attribute_value:
                raise Exception(f"Attribute value '{attribute_value}' not found for attribute '{attribute_name}'.")
            attribute_value_entities.append(product_attribute_value)

        product_option = await self.find_option_by_attribute_values(product, attribute_value_entities)
        if not product_option:
            raise Exception("No matching product option found for the provided attributes.")
        return product_option
