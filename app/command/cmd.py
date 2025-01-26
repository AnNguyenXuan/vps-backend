import sys
import os

# Thêm thư mục gốc (sample) vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.configuration.database import db
from app.models.user import User
from app.models.product import Product

import asyncio

async def create_tables():
    await db.set_bind("postgresql+asyncpg://thang:123456@localhost:5433/sample_fastapi")
    await db.gino.create_all()

asyncio.run(create_tables())
