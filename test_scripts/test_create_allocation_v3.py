from server.routers.manager import create_allocation, AllocationCreateReq
from server.database import SessionLocal
from server import models
import datetime

db = SessionLocal()
man = db.query(models.User).filter(models.User.role == "MANAGER").first()

proj = db.query(models.Project).filter(models.Project.manager_id == man.id).first()
emp = db.query(models.Employee).first()

alloc_req = AllocationCreateReq(
    employee_id=emp.id,
    project_id=proj.id,  # Ensure this project belongs to man.id
    utilisation_percentage=20,
    from_date=datetime.date(2027, 2, 20),
    to_date=datetime.date(2027, 9, 20)
)

try:
    res = create_allocation(alloc_req, db, current_user=man)
    print("Success:", res)
except Exception as e:
    import traceback
    traceback.print_exc()

db.close()
