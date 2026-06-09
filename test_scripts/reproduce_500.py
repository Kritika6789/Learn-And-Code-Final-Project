import requests
import sqlite3

BASE_URL = "http://127.0.0.1:8000/api"

# Get a manager
conn = sqlite3.connect("prm.db")
cur = conn.cursor()
cur.execute("SELECT id, username FROM users WHERE role='MANAGER' LIMIT 1")
man = cur.fetchone()
conn.close()

if not man:
    print("No manager found")
    exit()

man_id, man_user = man

# force login
res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "NewAdmin@123"})
admin_token = res.json().get("access_token")

# Create a project
res = requests.post(
    f"{BASE_URL}/admin/projects",
    json={"name":"Proj2", "start_date":"2026-06-08", "end_date":"2026-06-09", "status":"ACTIVE", "manager_id": man_id},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if "id" not in res.json():
    print("Project creation failed", res.text)
    exit()
proj_id = res.json()["id"]

# Login as manager
res = requests.post(f"{BASE_URL}/auth/login", data={"username": man_user, "password": "NewAdmin@123"})
if "access_token" not in res.json():
    # Maybe password is password123
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": man_user, "password": "password123"})
    if "access_token" not in res.json():
        print("Manager login failed", res.text)
        exit()
man_token = res.json()["access_token"]

# Create an allocation outside project dates
res = requests.post(
    f"{BASE_URL}/manager/allocations",
    json={"employee_id": 1, "project_id": proj_id, "utilisation_percentage": 20, "from_date": "2027-02-20", "to_date": "2027-09-20"},
    headers={"Authorization": f"Bearer {man_token}"}
)

print("STATUS:", res.status_code)
print("BODY:", res.text)
