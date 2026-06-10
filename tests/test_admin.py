import pytest

def test_create_user(client_admin):
    # Test creating a new user (Admin Route)
    payload = {
        "full_name": "Test User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123",
        "role": "EMPLOYEE"
    }
    response = client_admin.post("/api/admin/users", json=payload)
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
    response = client_admin.post("/api/admin/projects", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_deactivate_employee_ends_allocations(client_admin, client_manager, db):
    # To test deactivation logic, we need an active allocation
    # Create project
    proj_res = client_admin.post("/api/admin/projects", json={
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
    alloc_res = client_manager.post("/api/manager/allocations", json=payload)
    
    # Now deactivate the employee via admin route
    deact_res = client_admin.put("/api/admin/employees/1/deactivate")
    assert deact_res.status_code == 200
    
    # Verify employee status is deactivated and allocation is ended
    from server import models
    db.expire_all()
    emp = db.query(models.Employee).filter(models.Employee.id == 1).first()
    assert emp.status == "BENCH"
    assert emp.user.is_active == False
    
    # Verify allocation is ended
    alloc = db.query(models.Allocation).filter(models.Allocation.employee_id == 1).first()
    # Should be set to yesterday, we just check it is not 2026-12-31
    assert str(alloc.to_date) != "2026-12-31"

def test_assign_skills(client_admin, db):
    # Get first employee
    res = client_admin.get("/api/admin/employees")
    emp_id = res.json()[0]["id"]
    
    # Assign skill
    payload = {"name": "Python", "category": "Programming", "proficiency_level": "Expert"}
    skill_res = client_admin.post(f"/api/admin/employees/{emp_id}/skills", json=payload)
    assert skill_res.status_code == 200
    
    get_res = client_admin.get(f"/api/admin/employees/{emp_id}/skills")
    skills = get_res.json()
    assert len(skills) > 0
    assert any(s["name"] == "Python" for s in skills)

def test_view_company_allocation_matrix(client_admin):
    res = client_admin.get("/api/admin/allocations")
    assert res.status_code == 200
    assert type(res.json()) is list

def test_configure_system_settings(client_admin):
    # Get config
    res = client_admin.get("/api/admin/config")
    assert res.status_code == 200
    
    # Update config
    update_res = client_admin.put("/api/admin/config/LLM_API_KEY?value=test_key_123")
    assert update_res.status_code == 200

def test_reset_password(client_admin, db):
    # Reset admin's own password for test
    res = client_admin.put("/api/admin/users/1/reset-password?temp_password=NewPassword123!")
    assert res.status_code == 200
    assert "Password reset for admin" in res.json()["message"]
