import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from server.main import app

def test_ai_skill_match_extracts_capacity_and_filters(client_admin, client_manager, db):
    # Setup test project
    proj_res = client_admin.post("/api/admin/projects", json={
        "name": "Manager Test Project 2",
        "description": "Test",
        "start_date": "2026-06-01",
        "end_date": "2026-12-31",
        "status": "ACTIVE",
        "manager_id": 2,
        "total_story_points": 0
    })
    project_id = proj_res.json()["id"]

    with patch("server.services.ai_matcher.LLMFactory.get_provider") as mock_get_provider:
        # Mock the provider
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        
        # We need side_effect because generate_content is called TWICE:
        # 1. Capacity extraction
        # 2. Main matching prompt
        
        mock_provider.generate_content.side_effect = [
            "50", # First call returns 50% capacity requirement
            "ID   Name           Skills Match           Availability   Reason\n1    Mock Emp      Java                   50%            Good fit." # Second call returns final table
        ]

        response = client_manager.post("/api/manager/ai/search", json={"project_id": project_id, "requirement": "Java developer for 50%"})
        
        # Verify
        assert response.status_code == 200
        assert "Mock Emp" in response.json()["results"]
        
        # Ensure the provider was called twice
        assert mock_provider.generate_content.call_count == 2
        
        # Verify the first prompt asked for utilization percentage
        first_prompt = mock_provider.generate_content.call_args_list[0][0][0]
        assert "Extract the required utilization percentage" in first_prompt
        
        # Verify the second prompt contained our pre-filtered candidates instruction
        second_prompt = mock_provider.generate_content.call_args_list[1][0][0]
        assert "with at least 50% free capacity" in second_prompt

def test_ai_skill_match_defaults_to_zero(client_admin, client_manager, db):
    # If the user doesn't specify hours, the system should default to 0 to consider everyone
    proj_res = client_admin.post("/api/admin/projects", json={
        "name": "Manager Test Project 3",
        "description": "Test",
        "start_date": "2026-06-01",
        "end_date": "2026-12-31",
        "status": "ACTIVE",
        "manager_id": 2,
        "total_story_points": 0
    })
    project_id = proj_res.json()["id"]

    with patch("server.services.ai_matcher.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        
        # Return something non-numeric so it falls back to 0
        mock_provider.generate_content.side_effect = [
            "No specific hours mentioned.", # First call (capacity)
            "ID   Name           Skills Match           Availability   Reason\n1    Mock Emp      Java                   0%            Good fit." # Second call
        ]

        response = client_manager.post("/api/manager/ai/search", json={"project_id": project_id, "requirement": "I want a java developer"})
        
        assert response.status_code == 200
        assert mock_provider.generate_content.call_count == 2
        
        # Verify the second prompt defaulted to 0% free capacity so it doesn't exclude anyone
        second_prompt = mock_provider.generate_content.call_args_list[1][0][0]
        assert "with at least 0% free capacity" in second_prompt
