import os
from sqlalchemy.orm import Session
from server.database import SessionLocal, engine, Base
from server import models
from server.auth import get_password_hash

def seed_admin():
    Base.metadata.create_all(bind=engine)  # ensure tables exist
    db: Session = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(models.User).filter(models.User.role == "ADMIN").first()
        if admin:
            print("Admin user already seeded.")
            return
        # Create admin user
        admin_user = models.User(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            role="ADMIN",
            password_hash=get_password_hash("Admin@123"),
            is_active=True,
            force_password_change=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Admin user created with id {admin_user.id}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
