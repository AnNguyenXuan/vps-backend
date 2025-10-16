from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.model.s3_account import S3Account
from app.core.database import AsyncSessionLocal
from app.core.crypto import encrypt
from app.core.exceptions import NotFoundError


class S3Repository:
    """
    Repository quản lý bảng s3_account
    - Tự mở và đóng session
    - Có rollback khi lỗi
    - Giữ phong cách đồng nhất với các repository khác
    """

    async def find_by_user(self, user_id: int) -> S3Account | None:
        """
        Lấy tài khoản S3 của user đang hoạt động.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(S3Account)
                .where(S3Account.user_id == user_id)
                .where(S3Account.is_active == True)
            )
            return result.scalar_one_or_none()

    async def create_or_update(self, user_id: int, endpoint: str, access_key: str, secret_key: str, placement_type: str) -> S3Account:
        """
        Tạo mới hoặc cập nhật tài khoản S3.
        Nếu user đã có tài khoản, cập nhật key và endpoint.
        """
        async with AsyncSessionLocal() as session:
            try:
                encrypted_access = encrypt(access_key)
                encrypted_secret = encrypt(secret_key)

                result = await session.execute(
                    select(S3Account)
                    .where(S3Account.user_id == user_id)
                    .where(S3Account.is_active == True)
                )
                account = result.scalar_one_or_none()

                if account:
                    account.endpoint = endpoint
                    account.access_key = encrypted_access
                    account.secret_key = encrypted_secret
                else:
                    account = S3Account(
                        user_id=user_id,
                        endpoint=endpoint,
                        access_key=encrypted_access,
                        secret_key=encrypted_secret,
                        placement_type=placement_type
                    )
                    session.add(account)

                await session.commit()
                await session.refresh(account)
                return account
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def deactivate(self, user_id: int) -> bool:
        """
        Vô hiệu hóa tài khoản S3 của user (is_active=False)
        """
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(S3Account).where(S3Account.user_id == user_id)
                )
                account = result.scalar_one_or_none()
                if not account:
                    raise NotFoundError("S3 account not found")

                account.is_active = False
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def activate(self, user_id: int) -> bool:
        """
        Kích hoạt tài khoản S3 của user (is_active=True)
        """
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(S3Account).where(S3Account.user_id == user_id)
                )
                account = result.scalar_one_or_none()
                if not account:
                    raise NotFoundError("S3 account not found")

                account.is_active = True
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                raise
