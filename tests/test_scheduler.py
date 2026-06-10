import pytest
from datetime import date, timedelta
from unittest.mock import patch
from server.scheduler import update_employee_statuses, flag_project_health
from server import models
from tests.conftest import TestingSessionLocal

@patch("server.scheduler.SessionLocal", new=TestingSessionLocal)
def test_update_employee_statuses(db):
    # Get employee (currently BENCH)
    emp = db.query(models.Employee).filter(models.Employee.id == 1).first()
    assert emp.status == "BENCH"
    
    # Create project and active allocation
    project = models.Project(
        name="Scheduler Test Project",
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=10),
        status="ACTIVE",
        manager_id=2
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    alloc = models.Allocation(
        employee_id=emp.id,
        project_id=project.id,
        utilisation_percentage=50,
        from_date=date.today() - timedelta(days=1),
        to_date=date.today() + timedelta(days=5)
    )
    db.add(alloc)
    db.commit()
    
    # Run scheduler
    update_employee_statuses()
    
    # Employee should now be ALLOCATED
    db.refresh(emp)
    assert emp.status == "ALLOCATED"
    
    # Now simulate the allocation expiring
    alloc.to_date = date.today() - timedelta(days=1)
    db.commit()
    
    # Run scheduler again
    update_employee_statuses()
    
    # Employee should be back on BENCH
    db.refresh(emp)
    assert emp.status == "BENCH"

@patch("server.scheduler.SessionLocal", new=TestingSessionLocal)
def test_flag_project_health_auto_activate(db):
    # Create a PLANNED project with start date = today
    project = models.Project(
        name="Activation Test Project",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=10),
        status="PLANNED",
        manager_id=2
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Run scheduler
    flag_project_health()
    
    db.refresh(project)
    assert project.status == "ACTIVE"
