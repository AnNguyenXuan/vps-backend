from pydantic import BaseModel


# Schema cho việc tạo review
class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    rating: int
    comment: str
