import sys
import os

# Thêm thư mục gốc (sample) vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.configuration.database import AsyncSessionLocal
