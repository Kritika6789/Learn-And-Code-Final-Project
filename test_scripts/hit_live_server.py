import requests

BASE_URL = "http://127.0.0.1:8000/api"

print("Logging in as Admin...")
res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "NewAdmin@123"})
admin_token = res.json().get("access_token")
if not admin_token: print("Failed Admin Login"); exit()

print("Creating Project...")
res = requests.post(
    f"{BASE_URL}/admin/projects",
    json={"name":"Proj500", "start_date":"2026-06-08", "end_date":"2026-06-09", "status":"ACTIVE", "manager_id": 4},
    headers={"Authorization": f"Bearer {admin_token}"}
)
proj_id = res.json().get("id")
if not proj_id: print("Failed Project", res.text); exit()

# We need to login as Manager 4. What is their username?
import sqlite3
conn = sqlite3.connect("prm.db")
cur = conn.cursor()
cur.execute("SELECT username FROM users WHERE id=4")
man_user = cur.fetchone()[0]
conn.close()

print(f"Logging in as Manager: {man_user}...")
res = requests.post(f"{BASE_URL}/auth/login", data={"username": man_user, "password": "NewAdmin@123"})
man_token = res.json().get("access_token")
if not man_token:
    # try other pass
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": man_user, "password": "password123"})
    man_token = res.json().get("access_token")

if not man_token: print("Failed Manager Login"); exit()

print("Creating Allocation...")
res = requests.post(
    f"{BASE_URL}/manager/allocations",
    json={"employee_id": 1, "project_id": proj_id, "utilisation_percentage": 20, "from_date": "2027-02-20", "to_date": "2027-09-20"},
    headers={"Authorization": f"Bearer {man_token}"}
)

print("STATUS:", res.status_code)
print("BODY:", res.text)
