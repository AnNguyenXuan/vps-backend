from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class BlacklistToken(Base):
    __tablename__ = "blacklist_tokens"

    id = Column(String(64), primary_key=True, unique=True)
    expires_at = Column(DateTime, nullable=False, server_default=func.now())
