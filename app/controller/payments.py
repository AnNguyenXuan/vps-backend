from fastapi import APIRouter, HTTPException
from app.models.payments import Payment
from app.schemas.payments import PaymentCreate


router = APIRouter()


@router.post("/payments/")
async def create_payment(payment: PaymentCreate):
    new_payment = await Payment.create(
        order_id=payment.order_id,
        payment_method=payment.payment_method,
        paid_amount=payment.paid_amount,
        payment_status="paid"
    )
    return {"id": new_payment.id, "payment_method": new_payment.payment_method}

@router.get("/payments/{payment_id}")
async def get_payment(payment_id: int):
    payment = await Payment.get(id=payment_id).prefetch_related('order')
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "id": payment.id,
        "payment_method": payment.payment_method,
        "paid_amount": payment.paid_amount,
        "order": {
            "id": payment.order.id,
            "total_amount": payment.order.total_amount
        }
    }

@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int):
    payment_to_delete = await Payment.get(id=payment_id)
    if not payment_to_delete:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    await payment_to_delete.delete()
    return {"msg": "Payment deleted successfully"}
