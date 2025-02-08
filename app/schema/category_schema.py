from pydantic import BaseModel, field_validator, StringConstraints
from typing_extensions import Annotated


class CategoryBase(BaseModel):
    name: Annotated[
        str, 
        StringConstraints(
            min_length=1, 
            max_length=100, 
            pattern=r"^[a-zA-Z0-9\s\-_&]+$"
        )
    ]
    description: Annotated[str, StringConstraints(max_length=500)] | None = None
    parent_id: int | None = None

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, value):
        """ parent_id nếu có thì phải là số nguyên dương """
        if value is not None and value <= 0:
            raise ValueError("parent_id phải là số nguyên dương")
        return value


class CategoryCreate(CategoryBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Điện thoại",
                "description": "Danh mục chứa các sản phẩm điện thoại di động",
                "parent_id": None
            }
        }
    }


class CategoryRead(CategoryBase):
    id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Điện thoại",
                "description": "Danh mục chứa các sản phẩm điện thoại di động",
                "parent_id": None
            }
        }
    }


class CategoryUpdate(CategoryBase):
    id: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Smartphone",
                "description": "Cập nhật danh mục điện thoại",
                "parent_id": None
            }
        }
    }

