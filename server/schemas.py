from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    force_password_change: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    full_name: str
    email: EmailStr
    department: str
    designation: str

class EmployeeCreate(EmployeeBase):
    user_id: int
    manager_id: Optional[int] = None

class EmployeeUpdate(BaseModel):
    department: Optional[str] = None
    designation: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    user_id: Optional[int]
    status: str

    class Config:
        from_attributes = True

# --- Skill Schemas ---
class SkillCreate(BaseModel):
    name: str
    category: str
    proficiency_level: str

class SkillResponse(SkillCreate):
    id: int
    employee_id: int

    class Config:
        from_attributes = True

# --- Project Schemas ---
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    status: str
    manager_id: int
    total_story_points: Optional[int] = 0

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    manager_id: Optional[int] = None
    total_story_points: Optional[int] = None

class ProjectResponse(ProjectCreate):
    id: int

    class Config:
        from_attributes = True

# --- Milestone Schemas ---
class MilestoneCreate(BaseModel):
    title: str
    due_date: date
    status: str
    story_points: Optional[int] = 0

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    story_points: Optional[int] = None

class MilestoneResponse(MilestoneCreate):
    id: int
    project_id: int

    class Config:
        from_attributes = True
        
# --- Allocation Schemas ---
class AllocationResponse(BaseModel):
    id: int
    employee_id: int
    project_id: int
    utilisation_percentage: int
    from_date: date
    to_date: date

    class Config:
        from_attributes = True
