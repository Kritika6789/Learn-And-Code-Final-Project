from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False) # ADMIN, MANAGER, EMPLOYEE
    is_active = Column(Boolean, default=True)
    force_password_change = Column(Boolean, default=True)

    employee = relationship("Employee", back_populates="user", uselist=False)
    managed_projects = relationship("Project", back_populates="manager")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    status = Column(String, default="BENCH") # BENCH, ALLOCATED, PARTIAL

    user = relationship("User", back_populates="employee")
    skills = relationship("Skill", back_populates="employee")
    allocations = relationship("Allocation", back_populates="employee")
    timesheets = relationship("Timesheet", back_populates="employee")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    proficiency_level = Column(String, nullable=False)

    employee = relationship("Employee", back_populates="skills")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="PLANNED") # PLANNED, ACTIVE, ON_HOLD
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    manager = relationship("User", back_populates="managed_projects")
    milestones = relationship("Milestone", back_populates="project")
    allocations = relationship("Allocation", back_populates="project")
    timesheets = relationship("Timesheet", back_populates="project")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, DONE

    project = relationship("Project", back_populates="milestones")

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    utilisation_percentage = Column(Integer, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    employee = relationship("Employee", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")

class Timesheet(Base):
    __tablename__ = "timesheets"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    hours_logged = Column(Integer, nullable=False)
    activity_tags = Column(String, nullable=False) # comma-separated
    status = Column(String, nullable=False, default="SUBMITTED") # SUBMITTED, MISSED

    employee = relationship("Employee", back_populates="timesheets")
    project = relationship("Project", back_populates="timesheets")

class SystemConfiguration(Base):
    __tablename__ = "system_configuration"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
