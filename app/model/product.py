from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    location_address = Column(String(255), nullable=False)
    
    # Cho phép nullable nếu category có thể null
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    # Relationship tới Category
    category = relationship("Category")
    
    popularity = Column(Integer, nullable=True)
    discount_percentage = Column(Integer, nullable=True, default=0)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_delete = Column(Boolean, default=False)
