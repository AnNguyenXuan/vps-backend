from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated
from datetime import datetime

class ProductBase(BaseModel):
    name: Annotated[
        str, 
        StringConstraints(
            min_length=1, 
            max_length=300, 
            strip_whitespace=True, 
            pattern=r"^[a-zA-Z0-9\s\-_&]+$"
        )
    ]
    description: Annotated[str, StringConstraints(max_length=1000)] | None = None
    location_address: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    category_id: int | None = None
    popularity: int = Field(default=0, ge=0)
    discount_percentage: int = Field(default=0, ge=0, le=100)
    is_active: bool = True
    is_delete: bool = False

class ProductCreate(ProductBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Laptop Dell XPS 15",
                "description": "Laptop cao cấp dành cho lập trình viên và designer.",
                "location_address": "Kho hàng Hà Nội",
                "category_id": 2,
                "popularity": 100,
                "discount_percentage": 10,
                "is_active": True,
                "is_delete": False
            }
        }
    }

class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Laptop Dell XPS 15",
                "description": "Laptop cao cấp dành cho lập trình viên và designer.",
                "location_address": "Kho hàng Hà Nội",
                "category_id": 2,
                "popularity": 100,
                "discount_percentage": 10,
                "is_active": True,
                "is_delete": False,
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-02-01T12:00:00"
            }
        }
    }
