from server.database import SessionLocal
from server import models, auth
import traceback

def run():
    db = SessionLocal()
    try:
        new_user = models.User(
            username="kashika2",
            email="kashika2@gmail.com",
            full_name="Kashika",
            department="Unassigned",
            designation="Unassigned",
            role="MANAGER",
            password_hash="dummy",
            is_active=True,
            force_password_change=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        if new_user.role in ["EMPLOYEE", "MANAGER"]:
            emp = models.Employee(
                user_id=new_user.id,
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
