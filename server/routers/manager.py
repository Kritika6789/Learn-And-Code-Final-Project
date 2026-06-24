from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from server import models, schemas, auth
from server.database import get_db
from server.dependencies import get_current_active_user, get_read_only_db
import importlib
from server.services.ai_matcher import GenericMatchingStrategy
from server.services.llm_factory import LLMFactory
from server.config import MAX_UTILIZATION_PERCENTAGE

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

class RoleDefinition(BaseModel):
    title: str
    requirement: str

class AITeamSearchReq(BaseModel):
    project_id: int
    team_requirement: str

# --- Employee Management ---
@router.post("/employees/{employee_id}/unfreeze")
def unfreeze_employee(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    emp = db.query(models.Employee).filter(
        models.Employee.id == employee_id,
        models.Employee.manager_id == current_user.id
    ).first()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found or not in your team.")
        
    emp.timesheet_frozen = False
    if hasattr(emp, "missing_timesheet_reminders"):
        emp.missing_timesheet_reminders = 0
        
    db.commit()
    return {"message": f"Successfully unfrozen timesheet access for {emp.full_name}."}

# --- Resource Dashboard ---
@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    employees = db.query(models.Employee).filter(models.Employee.manager_id == current_user.id).all()
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
            "current_utilisation": total_util,
            "timesheet_frozen": getattr(emp, "timesheet_frozen", False)
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
        
    if emp.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only allocate your own team members.")
        
    if alloc.to_date < alloc.from_date:
        raise HTTPException(status_code=400, detail="To Date cannot be before From Date.")
        
    overlapping = db.query(models.Allocation).filter(
        models.Allocation.employee_id == alloc.employee_id,
        models.Allocation.from_date <= alloc.to_date,
        models.Allocation.to_date >= alloc.from_date
    ).all()
    
    total_util = sum(a.utilisation_percentage for a in overlapping) + alloc.utilisation_percentage
    if total_util > MAX_UTILIZATION_PERCENTAGE:
        raise HTTPException(status_code=400, detail=f"Employee cannot be allocated more than {MAX_UTILIZATION_PERCENTAGE}% in this period. Overlapping util will be {total_util}%")
        
    if alloc.from_date < proj.start_date or alloc.to_date > proj.end_date:
        raise HTTPException(status_code=400, detail=f"Allocation dates ({alloc.from_date} to {alloc.to_date}) must be within project dates ({proj.start_date} to {proj.end_date}).")
        
    try:
        new_alloc = models.Allocation(
            employee_id=alloc.employee_id,
            project_id=alloc.project_id,
            utilisation_percentage=alloc.utilisation_percentage,
            from_date=alloc.from_date,
            to_date=alloc.to_date
        )
        db.add(new_alloc)
        
        if new_alloc.from_date <= date.today() <= new_alloc.to_date:
            emp.status = "ALLOCATED"
            
        db.commit()
        db.refresh(new_alloc)
        return new_alloc
    except Exception as e:
        db.rollback()
        print(f"Error creating allocation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.put("/allocations/{alloc_id}/end")
def end_allocation(alloc_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    alloc = db.query(models.Allocation).filter(models.Allocation.id == alloc_id).first()
    if not alloc:
        raise HTTPException(status_code=404, detail="Allocation not found")
        
    if alloc.project.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project's allocations")
        
    if alloc.employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only end allocations for your own team members.")
        
    from datetime import timedelta
    alloc.to_date = date.today() - timedelta(days=1)
    
    emp = alloc.employee
    today = date.today()
    other_active = [a for a in emp.allocations if a.id != alloc.id and a.to_date >= today]
    if not other_active:
        emp.status = "BENCH"
        
    db.commit()
    return {"message": "Allocation ended today"}

@router.get("/dashboard/{emp_id}")
def employee_drill_down(emp_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id, models.Employee.manager_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found or not in your team")
        
    today = date.today()
    active_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
    total_util = sum(a.utilisation_percentage for a in active_allocs)
    
    recent_timesheets = db.query(models.Timesheet).filter(models.Timesheet.employee_id == emp.id).order_by(models.Timesheet.week_start_date.desc()).limit(4).all()
    
    tags = set()
    for t in recent_timesheets:
        if t.activity_tags:
            for tag in t.activity_tags.split(","):
                tags.add(tag.strip())
                
    return {
        "id": emp.id,
        "name": emp.full_name,
        "department": emp.department,
        "current_utilisation": total_util,
        "status": "BENCH" if total_util == 0 else f"ALLOCATED ({total_util}%)",
        "skills": [s.name for s in emp.skills],
        "allocations": [{"project": a.project.name, "percentage": a.utilisation_percentage, "from": a.from_date, "to": a.to_date} for a in active_allocs],
        "recent_tags": list(tags) if tags else ["None"]
    }

# --- Projects ---
@router.get("/projects")
def my_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    projects = db.query(models.Project).filter(models.Project.manager_id == current_user.id).all()
    res = []
    for p in projects:
        health = "🟢 ON TRACK"
        today = date.today()
        
        # Check active allocations
        active_allocs = [a for a in p.allocations if a.to_date >= today]
        if not active_allocs:
            health = "🔴 AT RISK"
            
        # Check overdue milestones
        for m in p.milestones:
            if m.status != "DONE" and m.due_date < today:
                health = "🔴 AT RISK"
                break
                
        if health == "🟢 ON TRACK" and p.end_date < today and p.status != "COMPLETED":
             health = "🟡 ATTENTION"
        
        # Add basic project info plus health
        res.append({
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "end_date": p.end_date,
            "health": health
        })
    return res

@router.get("/projects/{project_id}")
def project_details(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id, models.Project.manager_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    health = "🟢 ON TRACK"
    risk_flags = []
    today = date.today()
    for m in proj.milestones:
        if m.status != "DONE" and m.due_date < today:
            health = "🔴 AT RISK"
            risk_flags.append(f"✗ {m.title} milestone is overdue")
            
    if not proj.allocations:
        health = "🔴 AT RISK"
        risk_flags.append("✗ No resources allocated")
    else:
        active = [a for a in proj.allocations if a.to_date >= today]
        if not active:
            health = "🔴 AT RISK"
            risk_flags.append("✗ All resources have been de-allocated")
        else:
            risk_flags.append("✓ Resources are allocated")
        
    if not [f for f in risk_flags if "✗" in f]:
         risk_flags.append("✓ All milestones on track")
         
    if health == "🟢 ON TRACK" and proj.end_date < today and proj.status != "COMPLETED":
        health = "🟡 ATTENTION"

    return {
        "id": proj.id,
        "name": proj.name,
        "status": proj.status,
        "end_date": proj.end_date,
        "health": health,
        "risk_flags": risk_flags,
        "milestones": [{"id": m.id, "title": m.title, "due_date": m.due_date, "status": m.status} for m in proj.milestones],
        "allocations": [{"id": a.id, "employee": a.employee.full_name, "percentage": a.utilisation_percentage, "from": a.from_date, "to": a.to_date} for a in proj.allocations if a.to_date >= today]
    }

@router.get("/employees/{emp_id}/utilization")
def get_employee_utilization(emp_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    today = date.today()
    current_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
    total_util = sum(a.utilisation_percentage for a in current_allocs)
    
    return {"id": emp.id, "name": emp.full_name, "current_utilisation": total_util}

# --- AI ---
def get_llm_api_key(db: Session):
    config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "LLM_API_KEY").first()
    return config.value if config else None

def get_llm_provider_name(db: Session):
    config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "LLM_PROVIDER").first()
    return config.value if config else "gemini"

def get_llm_host_url(db: Session):
    config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "LLM_HOST").first()
    return config.value if config else None

@router.post("/ai/search")
def ai_skill_match(req: AISearchReq, db: Session = Depends(get_read_only_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    api_key = get_llm_api_key(db)
    
    # Example of Repository pattern (SRP & DIP)
    from server.repositories.employee import EmployeeRepository
    emp_repo = EmployeeRepository(db)
    employees = emp_repo.get_all()
    
    provider_name = get_llm_provider_name(db)
    host_url = get_llm_host_url(db)
    try:
        provider = LLMFactory.get_provider(provider_name, host_url=host_url)
    except ValueError as e:
        return {"results": f"AI Error: {str(e)}"}
        
    # Step 1: Interpret required capacity
    capacity_prompt = f"Extract the required utilization percentage (0-100) from this requirement: '{req.requirement}'. If hours are mentioned (e.g. 10 hrs/week), assume 40 hours = 100%. If full-time or no specific time is mentioned, return 0 to consider all candidates. If it says 'at least X%', return X. Return ONLY the integer."
    try:
        req_capacity_str = provider.generate_content(capacity_prompt, api_key).strip()
        import re
        match = re.search(r'\d+', req_capacity_str)
        req_capacity = int(match.group()) if match else 0
    except Exception:
        req_capacity = 0

    candidates = []
    
    today = date.today()
    for emp in employees:
        current_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
        total_util = sum(a.utilisation_percentage for a in current_allocs)
        free_capacity = MAX_UTILIZATION_PERCENTAGE - total_util
        
        # Step 2: Pre-filter out anyone who is fully booked or doesn't have enough capacity
        if free_capacity >= req_capacity:
            skills = ", ".join([s.name for s in emp.skills])
            recent_tags = ", ".join([t.activity_tags for t in emp.timesheets[-4:]]) if emp.timesheets else "None"
            candidates.append(f"ID {emp.id}: {emp.full_name}. Free capacity: {free_capacity}%. Skills: {skills}. Recent activity: {recent_tags}")
            
    if not candidates:
        return {"results": f"No employees have the required free capacity ({req_capacity}%)."}
        
    candidates_text = "\n".join(candidates)
    
    # Step 3: Refined prompt to only return good matches
    alloc_suggestion = f"{req_capacity}%" if req_capacity > 0 else "their full available capacity"
    prompt = f"""
    The manager needs: "{req.requirement}"
    
    Here are the available candidates with at least {req_capacity}% free capacity:
    {candidates_text}
    
    Select and rank ALL the candidates who are a good skill match for the requirement. 
    Do NOT include any candidate who does not match the required skills.
    
    You MUST output a simple text table with exactly these headers:
    ID   Name           Skills Match           Availability   Reason
    
    For EVERY SINGLE MATCHING candidate, output a row. Under the 'ID' column, use their exact integer ID. In the 'Reason' column, explicitly state why they are a good fit and suggest an allocation level (e.g., '{alloc_suggestion}').
    Do not output rows for candidates with "No match". Do not add any other text before or after the table.
    """
    
    matcher = GenericMatchingStrategy(provider)
    result = matcher.match_skills(prompt, api_key)
    return {"results": result}

@router.post("/ai/team-search")
def ai_team_search(req: AITeamSearchReq, db: Session = Depends(get_read_only_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    
    employees = db.query(models.Employee).all()
    candidates = []
    today = date.today()
    for emp in employees:
        current_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
        total_util = sum(a.utilisation_percentage for a in current_allocs)
        free_capacity = MAX_UTILIZATION_PERCENTAGE - total_util
        skills = ", ".join([s.name for s in emp.skills])
        
        status = f"Available ({free_capacity}% free)" if free_capacity > 0 else "Fully Allocated"
        if free_capacity == 0 and current_allocs:
            max_to_date = max(a.to_date for a in current_allocs)
            status += f" until {max_to_date}"
            
        candidates.append(f"ID {emp.id}: {emp.full_name}. Skills: {skills}. Status: {status}")

    candidates_text = "\n".join(candidates)
    
    prompt = f"""
    The manager needs to staff a whole team based on this requirement:
    "{req.team_requirement}"
    
    Here is the global pool of employees:
    {candidates_text}
    
    Your task: Parse the requirement to identify all the separate roles needed (e.g. if they ask for "2 backend devs", you must create Role 1: Backend Dev, Role 2: Backend Dev). Then find the best matching employee for each role.
    
    You MUST output a clean, spaced-out text list format. DO NOT use markdown tables (no '|' or '---' characters).
    
    Rules:
    1. Do not assign the same person to more than one role. An employee can only be assigned if they are "Available".
    2. STRICT MATCHING: Do NOT assign an employee unless their skills strongly match the role's requirements. If no employee has the required skills, you MUST leave it unassigned.
    3. GLOBALLY OPTIMIZE: If an employee is qualified for multiple roles, assign them to the role that best utilizes their strongest skills to maximize the overall team quality.
    4. If the role is filled: briefly explain why they are a good match based on their specific skills.
    5. If the role CANNOT be filled (due to missing skills or unavailability), you MUST use one of these two exact phrases for the Reason:
       - "Gap: Nobody has the skill (so hire or train)."
       - "Gap: Someone has it but is allocated elsewhere until [Date] (so plan around their availability)."
       
    Example Output Format:
    Role: Senior Java Dev
    Assigned: ID 1: Priya Sharma
    Reason: Has Advanced Java skills and is 100% free.
    
    Role: DevOps Engineer
    Assigned: None
    Reason: Gap: Nobody has the skill (so hire or train).
    
    Role: QA Tester
    Assigned: None
    Reason: Gap: Someone has it but is allocated elsewhere until 2026-08-01 (so plan around their availability).
       
    Output ONLY this exact text structure. Do not add any other text before or after. Do not output JSON.
    """
    
    api_key = get_llm_api_key(db)
    provider_name = get_llm_provider_name(db)
    host_url = get_llm_host_url(db)
    
    try:
        provider = LLMFactory.get_provider(provider_name, host_url=host_url)
    except ValueError as e:
        return {"results": f"AI Error: {str(e)}"}
        
    matcher = GenericMatchingStrategy(provider)
    result = matcher.match_skills(prompt, api_key)
    return {"results": result}

@router.get("/ai/risk-summary/{project_id}")
def ai_risk_summary(project_id: int, db: Session = Depends(get_read_only_db), current_user: models.User = Depends(get_current_active_user)):
    check_manager(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id, models.Project.manager_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    milestones = "\n".join([f"- {m.title} (Due: {m.due_date}, Status: {m.status})" for m in proj.milestones])
    today = date.today()
    active_allocs = [a for a in proj.allocations if a.from_date <= today <= a.to_date]
    allocations = "\n".join([f"- {a.employee.full_name} ({a.utilisation_percentage}%)" for a in active_allocs])
    
    timesheets = db.query(models.Timesheet).filter(models.Timesheet.project_id == project_id).all()
    timesheet_summary = "\n".join([f"- {t.employee.full_name}: {t.hours_logged} hrs, tags: {t.activity_tags}" for t in timesheets[-10:]])
    
    timesheets = db.query(models.Timesheet).filter(models.Timesheet.project_id == project_id).all()
    timesheet_summary = "\n".join([f"- {t.employee.full_name}: {t.hours_worked} hrs, tags: {t.activity_tags}" for t in timesheets[-10:]])
    
    prompt = f"""
    Analyze the risk for project '{proj.name}' ending on {proj.end_date}.
    
    Milestones:
    {milestones}
    
    Allocations:
    {allocations}
    
    Recent Timesheets:
    {timesheet_summary if timesheet_summary else "No timesheets submitted yet."}
    
    Write a brief, plain-English paragraph summarizing any risks (e.g., overdue milestones, lack of resources, lack of timesheet activity). Do not dump raw data.
    """
    
    api_key = get_llm_api_key(db)
    provider_name = get_llm_provider_name(db)
    host_url = get_llm_host_url(db)
    if api_key and len(api_key) > 5:
        try:
            provider = LLMFactory.get_provider(provider_name, host_url=host_url)
            response_text = provider.generate_content(prompt, api_key)
            return {"summary": response_text}
        except Exception as e:
            return {"summary": f"AI Error: {str(e)}\n\nMock: The project looks on track but verify milestone deadlines."}
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
    res = [{"employee": t.employee.full_name, "project": t.project.name, "hours": t.hours_logged, "status": t.status, "week": t.week_start_date} for t in timesheets]
    
    if week:
        # Compute missed timesheets for the specific week
        submitted = {(t.employee_id, t.project_id) for t in timesheets}
        allocations = db.query(models.Allocation).filter(
            models.Allocation.project_id.in_(project_ids),
            models.Allocation.from_date <= week,
            models.Allocation.to_date >= week
        ).all()
        
        for a in allocations:
            if (a.employee_id, a.project_id) not in submitted:
                res.append({
                    "employee": a.employee.full_name,
                    "project": a.project.name,
                    "hours": 0,
                    "status": "MISSED ⚠",
                    "week": week
                })
                
    return res
