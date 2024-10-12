from pydantic import BaseModel
from typing import List



# Schema cho việc tạo đơn hàng
class OrderDetailCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    user_id: int
    details: List[OrderDetailCreate]
