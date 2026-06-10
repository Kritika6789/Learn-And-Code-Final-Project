import pytest
from datetime import date, timedelta

def setup_project_and_allocation(client_admin, client_manager, db):
    # Setup project
    proj_res = client_admin.post("/api/admin/projects", json={
        "name": "Employee Test Project",
        "description": "Test",
        "start_date": "2026-06-01",
        "end_date": "2026-12-31",
        "status": "ACTIVE",
        "manager_id": 2,
        "total_story_points": 0
    })
    project_id = proj_res.json()["id"]
    
    # Setup allocation
    alloc_res = client_manager.post("/api/manager/allocations", json={
        "employee_id": 1,
        "project_id": project_id,
        "utilisation_percentage": 100,
        "from_date": "2026-06-01",
        "to_date": "2026-12-31"
    })
    return project_id

def test_submit_valid_timesheet(client_admin, client_manager, client_employee, db):
    project_id = setup_project_and_allocation(client_admin, client_manager, db)
    
    # Calculate a valid Monday date
    today = date.today()
    last_monday = today - timedelta(days=today.weekday())
    monday_str = last_monday.strftime("%Y-%m-%d")
    
    payload = {
        "project_id": project_id,
        "week_start_date": monday_str,
        "hours_logged": 40,
        "activity_tags": "API Development"
    }
    
    response = client_employee.post("/api/employee/timesheets", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Timesheet submitted successfully"

def test_max_hours_validation(client_admin, client_manager, client_employee, db):
    project_id = setup_project_and_allocation(client_admin, client_manager, db)
    
    today = date.today()
    last_monday = today - timedelta(days=today.weekday())
    monday_str = last_monday.strftime("%Y-%m-%d")
    
    payload = {
        "project_id": project_id,
        "week_start_date": monday_str,
        "hours_logged": 45, # 100% utilisation = 40 hours max. 45 should fail.
        "activity_tags": "Overtime Development"
    }
    
    response = client_employee.post("/api/employee/timesheets", json=payload)
    assert response.status_code == 400
    assert "exceeds expected max" in response.json()["detail"].lower()

def test_monday_constraint(client_admin, client_manager, client_employee, db):
    project_id = setup_project_and_allocation(client_admin, client_manager, db)
    
    today = date.today()
    # Force a Tuesday
    tuesday = today - timedelta(days=today.weekday()) + timedelta(days=1)
    tuesday_str = tuesday.strftime("%Y-%m-%d")
    
    payload = {
        "project_id": project_id,
        "week_start_date": tuesday_str,
        "hours_logged": 20,
        "activity_tags": "API Development"
    }
    
    response = client_employee.post("/api/employee/timesheets", json=payload)
    assert response.status_code == 400
    assert "must be a monday" in response.json()["detail"].lower()
