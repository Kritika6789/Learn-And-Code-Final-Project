from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from server import models, schemas, auth
from server.database import get_db
from server.dependencies import get_current_active_user

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_active_user)]
)

def check_admin(user: models.User):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized. Admin role required.")

# --- Users Management ---
@router.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    db_user = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    auth.validate_password(user.password)
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        password_hash=hashed_pw,
        is_active=True,
        force_password_change=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Auto-create Employee profile for EMPLOYEE or MANAGER roles
    if new_user.role in ["EMPLOYEE", "MANAGER"]:
        emp = models.Employee(
            user_id=new_user.id,
            full_name=new_user.full_name,
            email=new_user.email,
            department="Unassigned",
            designation="Unassigned",
            status="BENCH"
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)
    return new_user

@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    return db.query(models.User).all()

@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.username} deactivated"}

@router.put("/users/{user_id}/reactivate")
def reactivate_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {user.username} reactivated"}

@router.put("/users/{user_id}/reset-password")
def reset_user_password(user_id: int, temp_password: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    auth.validate_password(temp_password)
    user.password_hash = auth.get_password_hash(temp_password)
    user.force_password_change = True
    db.commit()
    return {"message": f"Password reset for {user.username}"}

# --- Employees Management ---
@router.post("/employees", response_model=schemas.EmployeeResponse)
def add_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    
    # Check if user exists and is not admin
    user = db.query(models.User).filter(models.User.id == emp.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User ID not found")
    if user.role not in ["EMPLOYEE", "MANAGER"]:
        raise HTTPException(status_code=400, detail="Only EMPLOYEE or MANAGER roles can have employee profiles")
    if user.employee:
        raise HTTPException(status_code=400, detail="User already has an employee profile")

    new_emp = models.Employee(
        user_id=emp.user_id,
        full_name=emp.full_name,
        email=emp.email,
        department=emp.department,
        designation=emp.designation,
        status="BENCH"
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@router.get("/employees", response_model=List[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    return db.query(models.Employee).all()

@router.put("/employees/{emp_id}/deactivate")
def deactivate_employee(emp_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Deactivate linked user account
    if emp.user:
        emp.user.is_active = False
    
    # End all active allocations to today
    today = date.today()
    for alloc in emp.allocations:
        if alloc.to_date >= today:
            alloc.to_date = today
    
    emp.status = "BENCH"
    db.commit()
    return {"message": "Employee deactivated and active allocations ended"}

@router.put("/employees/{emp_id}/manager")
def assign_manager(emp_id: int, manager_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    emp = db.query(models.Employee).filter(models.Employee.user_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    manager = db.query(models.User).filter(models.User.id == manager_id, models.User.role == "MANAGER").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found or invalid role")
    
    emp.manager_id = manager.id
    db.commit()
    return {"message": f"Manager assigned to employee {emp.full_name}"}

# --- Skills Management ---
@router.post("/employees/{emp_id}/skills", response_model=schemas.SkillResponse)
def add_skill(emp_id: int, skill: schemas.SkillCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    new_skill = models.Skill(
        employee_id=emp_id,
        name=skill.name,
        category=skill.category,
        proficiency_level=skill.proficiency_level
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.get("/employees/{emp_id}/skills", response_model=List[schemas.SkillResponse])
def get_skills(emp_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    return db.query(models.Skill).filter(models.Skill.employee_id == emp_id).all()

# --- Projects Management ---
@router.post("/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    manager = db.query(models.User).filter(models.User.id == project.manager_id, models.User.role == "MANAGER").first()
    if not manager:
        raise HTTPException(status_code=400, detail="Invalid Manager ID or user is not a Manager")
    
    new_proj = models.Project(**project.model_dump())
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    return new_proj

@router.get("/projects")
def get_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    projects = db.query(models.Project).all()
    res = []
    for p in projects:
        completed_sp = sum(m.story_points for m in p.milestones if m.status == "DONE" and m.story_points)
        res.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "start_date": p.start_date,
            "manager_id": p.manager_id,
            "manager_name": p.manager.full_name if p.manager else "Unknown",
            "end_date": p.end_date,
            "status": p.status,
            "total_story_points": p.total_story_points or 0,
            "completed_story_points": completed_sp
        })
    return res

@router.get("/projects/{project_id}")
def get_project_details(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": proj.id,
        "name": proj.name,
        "status": proj.status,
        "end_date": proj.end_date,
        "total_story_points": proj.total_story_points or 0,
        "milestones": [{"id": m.id, "title": m.title, "due_date": m.due_date, "status": m.status, "story_points": m.story_points or 0} for m in proj.milestones]
    }

@router.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = project_update.model_dump(exclude_unset=True)
    if "manager_id" in update_data:
        manager = db.query(models.User).filter(models.User.id == update_data["manager_id"], models.User.role == "MANAGER").first()
        if not manager:
            raise HTTPException(status_code=400, detail="Invalid Manager ID or user is not a Manager")
            
    for key, value in update_data.items():
        setattr(proj, key, value)
        
    db.commit()
    db.refresh(proj)
    return proj

@router.post("/projects/{project_id}/milestones", response_model=schemas.MilestoneResponse)
def add_milestone(project_id: int, milestone: schemas.MilestoneCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    proj = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_ms = models.Milestone(project_id=project_id, **milestone.model_dump())
    db.add(new_ms)
    db.commit()
    db.refresh(new_ms)
    return new_ms

# --- System Configuration ---
@router.get("/config")
def get_config(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    configs = db.query(models.SystemConfiguration).all()
    return {c.key: c.value for c in configs}

@router.put("/config/{key}")
def update_config(key: str, value: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    conf = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == key).first()
    if not conf:
        conf = models.SystemConfiguration(key=key, value=value)
        db.add(conf)
    else:
        conf.value = value
    db.commit()
    return {"message": f"Updated {key}"}

@router.get("/allocations", response_model=List[schemas.AllocationResponse])
def get_all_allocations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    check_admin(current_user)
    return db.query(models.Allocation).all()
