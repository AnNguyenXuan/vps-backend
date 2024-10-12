from fastapi import APIRouter
from app.models.user import abcxyz  # Import model abcxyz
from fastapi import HTTPException

router = APIRouter()

@router.post("/users/")
async def create_user(username: str, email: str):
    user = await abcxyz.create(username=username, email=email)
    return {"id": user.id, "username": user.username}

@router.get("/users/")
async def get_users():
    users = await abcxyz.all()
    return users
