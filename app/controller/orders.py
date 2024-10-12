from fastapi import APIRouter, HTTPException
from app.models.orders import Order, OrderDetail
from app.schemas.orders import OrderCreate, OrderDetailCreate


router = APIRouter()


@router.post("/orders/")
async def create_order(order: OrderCreate):
    new_order = await Order.create(
        user_id=order.user_id,
        total_amount=sum(item.price * item.quantity for item in order.details),
        status="processing"
    )
    
    # Tạo các chi tiết đơn hàng
    for item in order.details:
        await OrderDetail.create(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
    
    return {"id": new_order.id, "total_amount": new_order.total_amount}

@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = await Order.get(id=order_id).prefetch_related('user', 'order_details__product')
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "id": order.id,
        "user": {
            "id": order.user.id,
            "username": order.user.username
        },
        "total_amount": order.total_amount,
        "status": order.status,
        "details": [
            {
                "product_name": detail.product.name,
                "quantity": detail.quantity,
                "price": detail.price
            } for detail in order.order_details
        ]
    }

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    order_to_delete = await Order.get(id=order_id)
    if not order_to_delete:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await order_to_delete.delete()
    return {"msg": "Order deleted successfully"}
