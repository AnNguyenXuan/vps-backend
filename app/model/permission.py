from sqlalchemy import Column, Integer, String, Text, Boolean
from app.core.database import Base

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    default = Column(Boolean, nullable=False, default=False)
