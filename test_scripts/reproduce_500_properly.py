from fastapi.testclient import TestClient
from server.main import app
from server.database import SessionLocal
from server import models
from server.auth import create_access_token
from datetime import timedelta

client = TestClient(app)
db = SessionLocal()

# Get manager user
manager = db.query(models.User).filter(models.User.role == "MANAGER").first()
if not manager:
    print("No manager")
    exit(1)

# Generate manager token directly
access_token_expires = timedelta(minutes=30)
man_token = create_access_token(
    data={"sub": manager.username, "role": manager.role, "force_password_change": manager.force_password_change, "user_id": manager.id}, 
    expires_delta=access_token_expires
)

# Get admin user
admin = db.query(models.User).filter(models.User.role == "ADMIN").first()
admin_token = create_access_token(
    data={"sub": admin.username, "role": admin.role, "force_password_change": admin.force_password_change, "user_id": admin.id}, 
    expires_delta=access_token_expires
)

# Create Project via admin
res = client.post(
    "/api/admin/projects",
    json={"name":"TestProj500", "start_date":"2026-06-08", "end_date":"2026-06-09", "status":"ACTIVE", "manager_id": manager.id},
    headers={"Authorization": f"Bearer {admin_token}"}
)
proj_id = res.json()["id"]

# Create Allocation via manager
res = client.post(
    "/api/manager/allocations",
    json={"employee_id": 1, "project_id": proj_id, "utilisation_percentage": 20, "from_date": "2027-02-20", "to_date": "2027-09-20"},
    headers={"Authorization": f"Bearer {man_token}"}
)

print("STATUS:", res.status_code)
print("BODY:", res.text)
