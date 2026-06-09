from fastapi.testclient import TestClient
from server.database import SessionLocal
from server import models
import httpx

db = SessionLocal()
man = db.query(models.User).filter(models.User.role == "MANAGER").first()

proj = db.query(models.Project).filter(models.Project.manager_id == man.id).first()
if not proj:
    import datetime
    proj = models.Project(id=500, name="Proj", start_date=datetime.date(2026, 6, 8), end_date=datetime.date(2026, 6, 9), status="ACTIVE", manager_id=man.id)
    db.add(proj)
    db.commit()

emp = db.query(models.Employee).first()

db.close()

# We will just start the server using subprocess and send the request using httpx
import subprocess
import time
proc = subprocess.Popen(["python", "-m", "uvicorn", "server.main:app", "--port", "8003"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

for _ in range(15):
    try:
        res = httpx.get("http://127.0.0.1:8003/")
        if res.status_code == 200: break
    except:
        time.sleep(1)

# Now log in
import requests
# login bypass
res = requests.post("http://127.0.0.1:8003/api/auth/login", data={"username": man.username, "password": "NewAdmin@123"})
if res.status_code != 200:
    res = requests.post("http://127.0.0.1:8003/api/auth/login", data={"username": man.username, "password": "password123"})
token = res.json()["access_token"]

# create allocation
res = requests.post(
    "http://127.0.0.1:8003/api/manager/allocations",
    json={
        "employee_id": emp.id,
        "project_id": proj.id,
        "utilisation_percentage": 20,
        "from_date": "2027-02-20",
        "to_date": "2027-09-20"
    },
    headers={"Authorization": f"Bearer {token}"}
)

print("STATUS:", res.status_code)
print("BODY:", res.text)

proc.terminate()
stdout, stderr = proc.communicate()
print("STDERR:", stderr)
