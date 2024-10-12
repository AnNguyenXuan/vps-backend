from pydantic import BaseModel


# Schema cho việc tạo sản phẩm
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category_id: int
