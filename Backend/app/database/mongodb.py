from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

MONGODB_URL = settings.MONGODB_URL

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

def get_mongodb_db():
    """
    Trả về instance database của MongoDB (Async).
    Sử dụng Motor để tối ưu hóa bất đồng bộ với FastAPI.
    """
    if db_instance.client is None:
        db_instance.client = AsyncIOMotorClient(MONGODB_URL)
        
        # Trích xuất tên database từ URL kết nối
        db_name = "chat_db"
        if "/" in MONGODB_URL:
            parts = MONGODB_URL.split("/")
            if len(parts) > 3:
                last_part = parts[-1]
                db_name = last_part.split("?")[0] if "?" in last_part else last_part
                
        db_instance.db = db_instance.client[db_name or "chat_db"]
        
    return db_instance.db
