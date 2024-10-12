from fastapi import APIRouter
from app.models.users import User  # Import model User
from fastapi import HTTPException

router = APIRouter()

@router.post("/users/")
async def create_user(username: str, email: str):
    user = await User.create(username=username, email=email)
    return {"id": user.id, "username": user.username}

@router.get("/users/")
async def get_users():
    users = await User.all()
    return users

