from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Khởi tạo SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Tự động ping để kiểm tra kết nối còn sống không
    pool_size=10,  # Số lượng kết nối tối đa giữ trong pool
    max_overflow=20,  # Số kết nối vượt mức cho phép khi cao điểm
)

# Khởi tạo SessionLocal để tạo các session giao dịch ngắn hạn
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Định nghĩa Base class dùng chung cho các model
Base = declarative_base()


def get_db():
    """
    Dependency helper cung cấp Database Session cho FastAPI routes.
    Tự động đóng session sau khi xử lý xong request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
