import pytest
from unittest.mock import patch

def setup_project_and_employee(client_admin, db):
    # Setup test project
    proj_res = client_admin.post("/api/admin/projects", json={
        "name": "Manager Test Project",
        "description": "Test",
        "start_date": "2026-06-01",
        "end_date": "2026-12-31",
        "status": "ACTIVE",
        "manager_id": 2,
        "total_story_points": 0
    })
    print("PROJ_RES:", proj_res.json())
    project_id = proj_res.json()["id"]
    return project_id

def test_allocation_bounds(client_admin, client_manager, db):
    project_id = setup_project_and_employee(client_admin, db)
    
    # Try allocating outside project dates
    payload = {
        "employee_id": 1,
        "project_id": project_id,
        "utilisation_percentage": 50,
        "from_date": "2025-01-01",  # Before project start
        "to_date": "2026-12-31"
    }
    response = client_manager.post("/api/manager/allocations", json=payload)
    assert response.status_code == 400
    assert "must be within project dates" in response.json()["detail"]

def test_allocation_limits(client_admin, client_manager, db):
    project_id = setup_project_and_employee(client_admin, db)
    
    # Try allocating > 100%
    payload = {
        "employee_id": 1,
        "project_id": project_id,
        "utilisation_percentage": 110,
        "from_date": "2026-06-01",
        "to_date": "2026-12-31"
    }
    response = client_manager.post("/api/manager/allocations", json=payload)
    assert response.status_code == 400
    assert "Employee cannot be allocated more than 100%" in response.json()["detail"]

@patch("server.routers.manager.genai.GenerativeModel")
def test_ai_skill_matching(mock_genai, client_admin, client_manager, db):
    project_id = setup_project_and_employee(client_admin, db)
    # Mock the Gemini API response
    mock_instance = mock_genai.return_value
    mock_response = type("MockResponse", (), {"text": "1, Employee User, 85%, Java, High"})
    mock_instance.generate_content.return_value = mock_response

    response = client_manager.post("/api/manager/ai/search", json={"project_id": project_id, "requirement": "Java skills"})
    assert response.status_code == 200
    # The endpoint parses the raw text and returns a list of dictionaries if successful
    # Depending on how the frontend parses it, it might just return the raw text.
    # In our implementation, it returns {"matches": result.text}
    assert "Employee User" in response.json()["results"]
