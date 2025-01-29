from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    location_address: str
    category_id: int
    popularity: int | None = None
    is_active: bool = True
    is_delete: bool = True

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
