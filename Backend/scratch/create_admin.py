from app.database.mysql import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()
try:
    admin = db.query(User).filter(User.email == "admin@edumind.com").first()
    if not admin:
        admin = User(
            email="admin@edumind.com",
            password_hash=hash_password("adminpassword"),
            full_name="System Admin",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created successfully!")
    else:
        # Đảm bảo role là admin và active
        admin.role = "admin"
        admin.is_active = True
        db.commit()
        print("Admin user already exists, verified role and active status.")
finally:
    db.close()
