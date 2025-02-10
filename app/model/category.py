from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Thiết lập quan hệ tự tham chiếu:
    # - Mỗi Category có thể có một Category cha (parent).
    # - Thuộc tính 'children' được tự động tạo thông qua backref, chứa danh sách các Category con.
    parent = relationship("Category", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
