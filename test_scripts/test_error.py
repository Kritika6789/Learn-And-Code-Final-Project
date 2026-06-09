import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Login as admin to get admin token
res = requests.post(f"{BASE_URL}/auth/login", data={"username":"admin", "password":"NewAdmin@123"})
if res.status_code != 200:
    print("Admin login failed", res.text)
    exit(1)
admin_token = res.json()["access_token"]

# Create a project with dates 2026-06-08 to 2026-06-09
res = requests.post(
    f"{BASE_URL}/admin/projects",
    json={"name":"TestProjectDates", "start_date":"2026-06-08", "end_date":"2026-06-09", "status":"ACTIVE", "manager_id":4},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if res.status_code != 200:
    print("Project creation failed", res.text)
    exit(1)
proj_id = res.json()["id"]

# Login as manager 4 (assuming username man4 / NewAdmin@123 or similar, actually wait, the user's manager is User ID 4, maybe their username is manager or something).
# Let's just create an allocation directly in sqlite to see if it fails! No, the 500 error is from FastAPI.
