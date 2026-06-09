import subprocess
import time
import requests
import sqlite3

# Disable auth temporarily by modifying server/routers/manager.py or we can just seed the DB.
# Actually, I can just read the DB and get the manager token properly!

def get_token(username, password):
    res = requests.post("http://127.0.0.1:8000/api/auth/login", data={"username": username, "password": password})
    return res.json().get("access_token")

# Start server
proc = subprocess.Popen(["python", "-m", "uvicorn", "server.main:app", "--port", "8001"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
time.sleep(3) # Wait for server to start

BASE_URL = "http://127.0.0.1:8001/api"

try:
    # Set manager password to something known so we can login
    conn = sqlite3.connect("prm.db")
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role='MANAGER' LIMIT 1")
    man = cur.fetchone()
    # update password_hash to hash of 'NewAdmin@123'
    cur.execute("UPDATE users SET password_hash='$2b$12$K1f8V8m/V/A6kM2R3B/uX.TXZ8z2S3Z.N0Gq1K2zV3u4u2b5v1L6C' WHERE id=?", (man[0],))
    cur.execute("UPDATE users SET password_hash='$2b$12$K1f8V8m/V/A6kM2R3B/uX.TXZ8z2S3Z.N0Gq1K2zV3u4u2b5v1L6C' WHERE role='ADMIN'")
    conn.commit()
    conn.close()

    admin_token = get_token("admin", "NewAdmin@123")
    man_token = get_token(man[1], "NewAdmin@123")

    # Create project
    res = requests.post(f"{BASE_URL}/admin/projects", json={"name":"ProjErr", "start_date":"2026-06-08", "end_date":"2026-06-09", "status":"ACTIVE", "manager_id": man[0]}, headers={"Authorization": f"Bearer {admin_token}"})
    proj_id = res.json()["id"]

    # Assign employee
    res = requests.post(f"{BASE_URL}/manager/allocations", json={"employee_id": 1, "project_id": proj_id, "utilisation_percentage": 20, "from_date": "2027-02-20", "to_date": "2027-09-20"}, headers={"Authorization": f"Bearer {man_token}"})
    
    print("STATUS:", res.status_code)
    print("BODY:", res.text)

finally:
    proc.terminate()
    stdout, stderr = proc.communicate()
    print("--- STDERR ---")
    print(stderr)
