from database import engine, SessionLocal, Base
import models
import hashlib

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    db = SessionLocal()
    
    # Check if admin exists
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user:
        print("Seeding initial admin user...")
        # Simple SHA-256 hash for seed admin password (will use passlib in the app later)
        hashed_pw = hashlib.sha256("Admin@1234".encode()).hexdigest()
        admin = models.User(
            username="admin",
            email="admin@techserve.com",
            password_hash=hashed_pw,
            full_name="System Administrator",
            role="ADMIN",
            is_active=True,
            force_password_change=True
        )
        db.add(admin)
    
    # Seed default configurations
    configs = {
        "LLM_PROVIDER": "Google Gemini",
        "LLM_API_KEY": "",
        "SCHEDULER_INTERVAL_HOURS": "4",
        "MAX_WEEKLY_HOURS": "40"
    }
    
    for key, value in configs.items():
        config_entry = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == key).first()
        if not config_entry:
            db.add(models.SystemConfiguration(key=key, value=value))

    db.commit()
    db.close()
    print("Database seeding complete.")

if __name__ == "__main__":
    init_db()
