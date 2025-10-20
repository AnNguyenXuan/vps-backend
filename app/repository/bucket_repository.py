from sqlalchemy import select
from app.model.bucket_account import BucketAccount
from app.core.database import AsyncSessionLocal

class BucketAccountRepository:
    async def get_by_user(self, user_id: int) -> BucketAccount | None:
        async with AsyncSessionLocal() as s:
            rs = await s.execute(select(BucketAccount).where(BucketAccount.user_id==user_id))
            return rs.scalar_one_or_none()

    async def upsert(self, user_id: int, access_key_enc: str, secret_key_enc: str) -> BucketAccount:
        async with AsyncSessionLocal() as s:
            row = await s.get(BucketAccount, user_id)
            if row is None:
                row = BucketAccount(
                    user_id=user_id,
                    access_key_enc=access_key_enc,
                    secret_key_enc=secret_key_enc
                )
                s.add(row)
            else:
                row.access_key_enc = access_key_enc
                row.secret_key_enc = secret_key_enc
            await s.commit()
            await s.refresh(row)
            return row
