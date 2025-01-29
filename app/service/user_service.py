from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UserCreate

class UserService:
    def __init__(self):
        self.repository = UserRepository()

    async def create_new_user(self, db: AsyncSession, user: UserCreate):
        return await self.repository.create_user(db, user)

    async def fetch_user_by_id(self, db: AsyncSession, user_id: int):
        return await self.repository.get_user_by_id(db, user_id)


