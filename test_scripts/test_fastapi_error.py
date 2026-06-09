from fastapi.testclient import TestClient
from server.main import app
from server import models
from server.database import SessionLocal

client = TestClient(app)
db = SessionLocal()

# Seed a user if needed or just use auth login
res = client.post("/api/auth/login", data={"username": "admin", "password": "NewAdmin@123"})
admin_token = res.json()["access_token"]

res = client.post(
    "/api/admin/projects",
    json={"name":"TestProj2", "start_date":"2026-06-08", "end_date":"2026-06-09", "status":"ACTIVE", "manager_id":4},
    headers={"Authorization": f"Bearer {admin_token}"}
)
proj_id = res.json()["id"]

# Login as manager 4 (find their username)
user4 = db.query(models.User).filter(models.User.id == 4).first()
res = client.post("/api/auth/login", data={"username": user4.username, "password": "password123"})
if res.status_code != 200:
    # Try getting temp_pw if they never logged in. Let's force set password
    user4.password_hash = "$2b$12$K1f8V8m/V/A6kM2R3B/uX.TXZ8z2S3Z.N0Gq1K2zV3u4u2b5v1L6C" # hashed NewAdmin@123
    db.commit()
    res = client.post("/api/auth/login", data={"username": user4.username, "password": "NewAdmin@123"})

man_token = res.json()["access_token"]

# Create employee 1 if missing
if not db.query(models.Employee).filter(models.Employee.id == 1).first():
    db.add(models.Employee(id=1, full_name="Kanika", email="kanika@example.com", department="IT", designation="Dev"))
    db.commit()

res = client.post(
    "/api/manager/allocations",
    json={"employee_id": 1, "project_id": proj_id, "utilisation_percentage": 20, "from_date": "2027-02-20", "to_date": "2027-09-20"},
    headers={"Authorization": f"Bearer {man_token}"}
)
print("STATUS CODE:", res.status_code)
print("RESPONSE BODY:", res.text)
