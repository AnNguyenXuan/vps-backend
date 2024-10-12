from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    paid_amount: float
