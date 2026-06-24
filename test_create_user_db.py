from server.database import SessionLocal
from server import models, auth
import traceback

def run():
    db = SessionLocal()
    try:
        user = models.User(
            username="testing3",
            email="testing3@gmail.com",
            full_name="test3",
            role="MANAGER",
            password_hash="dummy",
            is_active=True,
            force_password_change=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        emp = models.Employee(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            department="Unassigned",
            designation="Unassigned",
            status="BENCH"
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)
        print("Success")
    except Exception as e:
        print("Error:")
        traceback.print_exc()

if __name__ == "__main__":
    run()
