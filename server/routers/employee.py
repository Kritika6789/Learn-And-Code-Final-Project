from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from server import models, schemas, auth
from server.database import get_db
from server.dependencies import get_current_active_user

router = APIRouter(
    prefix="/api/employee",
    tags=["employee"],
    dependencies=[Depends(get_current_active_user)]
)

def get_employee_profile(user: models.User, db: Session):
    if user.role != "EMPLOYEE":
        raise HTTPException(status_code=403, detail="Not authorized. Employee role required.")
    emp = db.query(models.Employee).filter(models.Employee.user_id == user.id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found for this user.")
    return emp

class TimesheetCreateReq(BaseModel):
    project_id: int
    week_start_date: date
    hours_logged: int
    activity_tags: str

@router.post("/timesheets")
def submit_timesheet(ts: TimesheetCreateReq, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    emp = get_employee_profile(current_user, db)
    
    if ts.week_start_date.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start_date must be a Monday")
    if ts.week_start_date > date.today():
        raise HTTPException(status_code=400, detail="Cannot submit timesheet for a future week")
        
    alloc = db.query(models.Allocation).filter(
        models.Allocation.employee_id == emp.id,
        models.Allocation.project_id == ts.project_id,
        models.Allocation.from_date <= ts.week_start_date,
        models.Allocation.to_date >= ts.week_start_date
    ).first()
    
    if not alloc:
        raise HTTPException(status_code=400, detail="You are not allocated to this project for the specified week")
        
    config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "MAX_WEEKLY_HOURS").first()
    max_weekly_hours = int(config.value) if config else 40
    
    allowed_hours = (alloc.utilisation_percentage / 100.0) * max_weekly_hours
    if ts.hours_logged > allowed_hours:
        raise HTTPException(status_code=400, detail=f"Hours logged ({ts.hours_logged}) exceeds expected max for this project ({allowed_hours})")
        
    existing_ts = db.query(models.Timesheet).filter(
        models.Timesheet.employee_id == emp.id,
        models.Timesheet.week_start_date == ts.week_start_date
    ).all()
    
    total_logged = sum(t.hours_logged for t in existing_ts)
    if total_logged + ts.hours_logged > max_weekly_hours:
        raise HTTPException(status_code=400, detail=f"Total hours for the week would exceed system maximum ({max_weekly_hours})")
        
    for t in existing_ts:
        if t.project_id == ts.project_id:
            raise HTTPException(status_code=400, detail="Timesheet already submitted for this project and week")
            
    new_ts = models.Timesheet(
        employee_id=emp.id,
        project_id=ts.project_id,
        week_start_date=ts.week_start_date,
        hours_logged=ts.hours_logged,
        activity_tags=ts.activity_tags,
        status="SUBMITTED"
    )
    db.add(new_ts)
    db.commit()
    db.refresh(new_ts)
    return {"message": "Timesheet submitted successfully", "id": new_ts.id}

@router.get("/timesheets")
def my_timesheets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    emp = get_employee_profile(current_user, db)
    timesheets = db.query(models.Timesheet).filter(models.Timesheet.employee_id == emp.id).order_by(models.Timesheet.week_start_date.desc()).all()
    
    weeks = {}
    for t in timesheets:
        w = str(t.week_start_date)
        if w not in weeks:
            weeks[w] = {"week_start": w, "total_hrs": 0, "status": "SUBMITTED"}
        weeks[w]["total_hrs"] += t.hours_logged
        
    return list(weeks.values())

@router.get("/allocations")
def my_allocations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    emp = get_employee_profile(current_user, db)
    allocs = db.query(models.Allocation).filter(models.Allocation.employee_id == emp.id).all()
    return [{
        "project": a.project.name,
        "percentage": a.utilisation_percentage,
        "from": a.from_date,
        "to": a.to_date,
        "status": "ACTIVE" if a.from_date <= date.today() <= a.to_date else "PAST/FUTURE"
    } for a in allocs]
