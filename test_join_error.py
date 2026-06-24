from server.database import SessionLocal
from server import models
import traceback

def run():
    db = SessionLocal()
    try:
        res = db.query(models.Employee).join(models.User, models.Employee.user_id == models.User.id).filter(models.User.role == "EMPLOYEE").all()
        print("Success, found", len(res))
    except Exception as e:
        print("Error:")
        traceback.print_exc()

if __name__ == "__main__":
    run()
