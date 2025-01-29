from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model.user import User
from app.schema.user_schema import UserCreate

class UserRepository:
    async def create_user(self, db: AsyncSession, user: UserCreate):
        hashed_pw = user.password  # Cần hash trước khi lưu
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_pw,
            phone=user.phone,
            address=user.address,
            is_active=user.is_active,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
