from server.routers.manager import create_allocation, AllocationCreateReq
from server.database import SessionLocal
from server import models

db = SessionLocal()
man = db.query(models.User).filter(models.User.role == "MANAGER").first()
alloc_req = AllocationCreateReq(
    employee_id=1,
    project_id=1,  # Ensure this project belongs to man.id
    utilisation_percentage=20,
    from_date="2027-02-20",
    to_date="2027-09-20"
)

# First create a project so it doesn't fail on project check
if not db.query(models.Project).filter(models.Project.id == 1, models.Project.manager_id == man.id).first():
    proj = models.Project(id=1, name="Proj", start_date="2026-06-08", end_date="2026-06-09", status="ACTIVE", manager_id=man.id)
    db.add(proj)
    db.commit()

# Ensure employee 1 exists
if not db.query(models.Employee).filter(models.Employee.id == 1).first():
    emp = models.Employee(id=1, full_name="Kanika", email="kanika@example.com", department="IT", designation="Dev")
    db.add(emp)
    db.commit()

try:
    res = create_allocation(alloc_req, db, current_user=man)
    print("Success:", res)
except Exception as e:
    import traceback
    traceback.print_exc()

db.close()
