import sys
sys.path.append('.')
from server.database import SessionLocal
from server import models
from datetime import date
from pydantic import BaseModel

class AllocationCreateReq(BaseModel):
    employee_id: int
    project_id: int
    utilisation_percentage: int
    from_date: date
    to_date: date

db = SessionLocal()

alloc = AllocationCreateReq(
    employee_id=1,
    project_id=1,
    utilisation_percentage=20,
    from_date="2027-02-20",
    to_date="2027-09-20"
)

try:
    proj = db.query(models.Project).filter(models.Project.id == alloc.project_id).first()
    emp = db.query(models.Employee).filter(models.Employee.id == alloc.employee_id).first()

    overlapping = db.query(models.Allocation).filter(
        models.Allocation.employee_id == alloc.employee_id,
        models.Allocation.from_date <= alloc.to_date,
        models.Allocation.to_date >= alloc.from_date
    ).all()

    total_util = sum(a.utilisation_percentage for a in overlapping) + alloc.utilisation_percentage
    if total_util > 100:
        print("400 Error")

    new_alloc = models.Allocation(**alloc.model_dump())
    db.add(new_alloc)

    if new_alloc.from_date <= date.today() <= new_alloc.to_date:
        emp.status = "ALLOCATED"

    db.commit()
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

db.close()
