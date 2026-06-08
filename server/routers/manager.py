from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

import models, schemas, auth
from database import get_db
from dependencies import get_current_active_user, get_read_only_db
import google.generativeai as genai

router = APIRouter(
    prefix="/api/manager",
    tags=["manager"],
    dependencies=[Depends(get_current_active_user)]
)

def check_manager(user: models.User):
    if user.role != "MANAGER":
        raise HTTPException(status_code=403, detail="Not authorized. Manager role required.")

class AllocationCreateReq(BaseModel):
    employee_id: int
    project_id: int
    utilisation_percentage: int
    from_date: date
    to_date: date

class AISearchReq(BaseModel):
    project_id: int
    requirement: str

# --- Resource Dashboard ---
@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    employees = db.query(models.Employee).all()
    bench = []
    active = []
    
    for emp in employees:
        today = date.today()
        current_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
        total_util = sum(a.utilisation_percentage for a in current_allocs)
        
        emp_data = {
            "id": emp.id,
            "name": emp.full_name,
            "department": emp.department,
            "skills": [s.name for s in emp.skills],
            "current_utilisation": total_util
        }
        
        if total_util == 0:
            bench.append(emp_data)
        else:
            active.append(emp_data)
            
    return {"bench": bench, "active": active}

# --- Allocations ---
@router.post("/allocations", response_model=schemas.AllocationResponse)
def create_allocation(alloc: AllocationCreateReq, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    proj = db.query(models.Project).filter(models.Project.id == alloc.project_id, models.Project.manager_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=403, detail="Project not found or not managed by you")
        
    emp = db.query(models.Employee).filter(models.Employee.id == alloc.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    overlapping = db.query(models.Allocation).filter(
        models.Allocation.employee_id == alloc.employee_id,
        models.Allocation.from_date <= alloc.to_date,
        models.Allocation.to_date >= alloc.from_date
    ).all()
    
    total_util = sum(a.utilisation_percentage for a in overlapping) + alloc.utilisation_percentage
    if total_util > 100:
        raise HTTPException(status_code=400, detail=f"Employee cannot be allocated more than 100% in this period. Overlapping util will be {total_util}%")
        
    new_alloc = models.Allocation(**alloc.model_dump())
    db.add(new_alloc)
    
    if new_alloc.from_date <= date.today() <= new_alloc.to_date:
        emp.status = "ALLOCATED"
        
    db.commit()
    db.refresh(new_alloc)
    return new_alloc

@router.put("/allocations/{alloc_id}/end")
def end_allocation(alloc_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    alloc = db.query(models.Allocation).filter(models.Allocation.id == alloc_id).first()
    if not alloc:
        raise HTTPException(status_code=404, detail="Allocation not found")
        
    if alloc.project.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project's allocations")
        
    alloc.to_date = date.today()
    db.commit()
    return {"message": "Allocation ended today"}

# --- Projects ---
@router.get("/projects", response_model=List[schemas.ProjectResponse])
def my_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    return db.query(models.Project).filter(models.Project.manager_id == current_user.id).all()

@router.get("/projects/{project_id}")
def project_details(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id, models.Project.manager_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {
        "id": proj.id,
        "name": proj.name,
        "status": proj.status,
        "end_date": proj.end_date,
        "milestones": [{"id": m.id, "title": m.title, "due_date": m.due_date, "status": m.status} for m in proj.milestones],
        "allocations": [{"id": a.id, "employee": a.employee.full_name, "percentage": a.utilisation_percentage, "from": a.from_date, "to": a.to_date} for a in proj.allocations]
    }

# --- AI ---
def get_llm_api_key(db: Session):
    config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "LLM_API_KEY").first()
    return config.value if config else None

@router.post("/ai/search")
def ai_skill_match(req: AISearchReq, db: Session = Depends(get_read_only_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    api_key = get_llm_api_key(db)
    
    employees = db.query(models.Employee).all()
    candidates = []
    
    today = date.today()
    for emp in employees:
        current_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
        total_util = sum(a.utilisation_percentage for a in current_allocs)
        free_capacity = 100 - total_util
        if free_capacity > 0:
            skills = ", ".join([s.name for s in emp.skills])
            recent_tags = ", ".join([t.activity_tags for t in emp.timesheets[-4:]]) if emp.timesheets else "None"
            candidates.append(f"ID {emp.id}: {emp.full_name}. Free capacity: {free_capacity}%. Skills: {skills}. Recent activity: {recent_tags}")
            
    if not candidates:
        return {"results": "No employees have free capacity."}
        
    candidates_text = "\n".join(candidates)
    
    prompt = f"""
    The manager needs: "{req.requirement}"
    
    Here are the available candidates:
    {candidates_text}
    
    Rank the top matches and provide a brief, plain-English reason for each based on their skills and availability.
    Format your response nicely.
    """
    
    if api_key and len(api_key) > 5:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction="You are a read-only Project Management AI Assistant. Your role is strictly to analyze data and provide insights. You do not have permission to modify, delete, or create data."
            )
            response = model.generate_content(prompt)
            return {"results": response.text}
        except Exception as e:
            return {"results": f"AI Error: {str(e)}\n\n(Mocked Results: Priya Sharma is a good match.)"}
    else:
        return {"results": "LLM_API_KEY is not configured in System Configuration. \n\nMocked Results: \n1. Priya Sharma - Good match based on skills."}

@router.get("/ai/risk-summary/{project_id}")
def ai_risk_summary(project_id: int, db: Session = Depends(get_read_only_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id, models.Project.manager_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    milestones = "\n".join([f"- {m.title} (Due: {m.due_date}, Status: {m.status})" for m in proj.milestones])
    allocations = "\n".join([f"- {a.employee.full_name} ({a.utilisation_percentage}%)" for a in proj.allocations])
    
    prompt = f"""
    Analyze the risk for project '{proj.name}' ending on {proj.end_date}.
    
    Milestones:
    {milestones}
    
    Allocations:
    {allocations}
    
    Write a brief, plain-English paragraph summarizing any risks (e.g., overdue milestones, lack of resources). Do not dump raw data.
    """
    
    api_key = get_llm_api_key(db)
    if api_key and len(api_key) > 5:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction="You are a read-only Project Management AI Assistant. Your role is strictly to analyze data and provide insights. You do not have permission to modify, delete, or create data."
            )
            response = model.generate_content(prompt)
            return {"summary": response.text}
        except Exception as e:
            return {"summary": f"AI Error: {str(e)}"}
    else:
        return {"summary": "LLM_API_KEY is not configured. \n\nMock: The project looks on track but verify milestone deadlines."}

@router.get("/timesheets")
def view_team_timesheets(week: Optional[date] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    projects = db.query(models.Project).filter(models.Project.manager_id == current_user.id).all()
    project_ids = [p.id for p in projects]
    
    query = db.query(models.Timesheet).filter(models.Timesheet.project_id.in_(project_ids))
    if week:
        query = query.filter(models.Timesheet.week_start_date == week)
        
    timesheets = query.all()
    return [{"employee": t.employee.full_name, "project": t.project.name, "hours": t.hours_logged, "status": t.status, "week": t.week_start_date} for t in timesheets]
