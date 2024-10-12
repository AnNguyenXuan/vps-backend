from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.controller import users, products, orders, reviews, payments, shipments

app = FastAPI()

# Đăng ký các routers từ các controllers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(shipments.router, prefix="/shipments", tags=["Shipments"])

# Kết nối với cơ sở dữ liệu PostgreSQL và đăng ký tất cả model
register_tortoise(
    app,
    db_url="postgres://Thang:123456@localhost:5432/dbname",
    modules={"models": ["app.models.users", "app.models.products", "app.models.orders", 
                        "app.models.payments", "app.models.shipments", "app.models.reviews"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
