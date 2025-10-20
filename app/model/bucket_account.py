from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, Text
from datetime import datetime

class Base(DeclarativeBase): pass

class BucketAccount(Base):
    __tablename__ = "bucket_account"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    access_key_enc: Mapped[str] = mapped_column(Text, nullable=False)
    secret_key_enc: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]