import pytest

def test_create_user(client_admin):
    # Test creating a new user (Admin Route)
    payload = {
        "full_name": "Test User",
        "email": "test@example.com",
        "username": "testuser",
        "role": "EMPLOYEE"
    }
    response = client_admin.post("/admin/users", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "EMPLOYEE"

def test_create_project(client_admin):
    # Test creating a project
    payload = {
        "name": "Test Project",
        "description": "Test Desc",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "status": "PLANNED",
        "manager_id": 2, # Manager user id from conftest
        "total_story_points": 100
    }
    response = client_admin.post("/admin/projects", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_deactivate_employee_ends_allocations(client_admin, db):
    # To test deactivation logic, we need an active allocation
    # Create project
    proj_res = client_admin.post("/admin/projects", json={
        "name": "Deactivation Project",
        "description": "",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "status": "ACTIVE",
        "manager_id": 2,
        "total_story_points": 0
    })
    project_id = proj_res.json()["id"]
    
    # We need to test the deactivate_employee endpoint but the emp exists
    # First allocate employee
    payload = {
        "employee_id": 1,
        "project_id": project_id,
        "utilisation_percentage": 50,
        "from_date": "2026-01-01",
        "to_date": "2026-12-31"
    }
    # Log in as manager to allocate
    manager_res = client_admin.post("/api/auth/login", data={"username": "manager", "password": "password"})
    mgr_token = manager_res.json()["access_token"]
    alloc_res = client_admin.post("/manager/allocations", json=payload, headers={"Authorization": f"Bearer {mgr_token}"})
    
    # Now deactivate the employee via admin route
    deact_res = client_admin.post("/admin/employees/1/deactivate")
    assert deact_res.status_code == 200
    
    # Verify employee status is deactivated and allocation is ended
    from server import models
    emp = db.query(models.Employee).filter(models.Employee.id == 1).first()
    assert emp.status == "DEACTIVATED"
    
    # Verify allocation is ended
    alloc = db.query(models.Allocation).filter(models.Allocation.employee_id == 1).first()
    # Should be set to yesterday, we just check it is not 2026-12-31
    assert str(alloc.to_date) != "2026-12-31"
