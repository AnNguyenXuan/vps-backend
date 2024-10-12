from fastapi import APIRouter, HTTPException
from app.models.reviews import Review
from app.schemas.reviews import ReviewCreate


router = APIRouter()


@router.post("/reviews/")
async def create_review(review: ReviewCreate):
    new_review = await Review.create(
        product_id=review.product_id,
        user_id=review.user_id,
        rating=review.rating,
        comment=review.comment
    )
    return {"id": new_review.id, "rating": new_review.rating, "comment": new_review.comment}

@router.get("/reviews/{review_id}")
async def get_review(review_id: int):
    review = await Review.get(id=review_id).prefetch_related('product', 'user')
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "product": {
            "id": review.product.id,
            "name": review.product.name
        },
        "user": {
            "id": review.user.id,
            "username": review.user.username
        }
    }

@router.delete("/reviews/{review_id}")
async def delete_review(review_id: int):
    review_to_delete = await Review.get(id=review_id)
    if not review_to_delete:
        raise HTTPException(status_code=404, detail="Review not found")
    
    await review_to_delete.delete()
    return {"msg": "Review deleted successfully"}
