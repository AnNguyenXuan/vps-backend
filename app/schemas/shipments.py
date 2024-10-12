from pydantic import BaseModel
from datetime import datetime

class ShipmentCreate(BaseModel):
    order_id: int
    shipping_address: str
    shipping_status: str
    shipped_at: datetime = None

class ShipmentOut(BaseModel):
    id: int
    order_id: int
    shipping_address: str
    shipping_status: str
    shipped_at: datetime = None

    class Config:
        from_attributes = True