from fastapi import APIRouter, HTTPException
from app.models.product import Product
from app.schemas.products import ProductCreate


router = APIRouter()


@router.post("/products/")
async def create_product(product: ProductCreate):
    new_product = await Product.create(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )
    return {"id": new_product.id, "name": new_product.name}

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    product = await Product.get(id=product_id).prefetch_related('category')
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category": product.category.name if product.category else None
    }

@router.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductCreate):
    product_to_update = await Product.get(id=product_id)
    if not product_to_update:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_to_update.name = product.name
    product_to_update.description = product.description
    product_to_update.price = product.price
    product_to_update.stock = product.stock
    product_to_update.category_id = product.category_id
    await product_to_update.save()
    return {"msg": "Product updated successfully"}

@router.delete("/products/{product_id}")
async def delete_product(product_id: int):
    product_to_delete = await Product.get(id=product_id)
    if not product_to_delete:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await product_to_delete.delete()
    return {"msg": "Product deleted successfully"}
