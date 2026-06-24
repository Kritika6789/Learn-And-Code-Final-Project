import requests

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = None

class APIError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def get_headers():
    if TOKEN:
        return {"Authorization": f"Bearer {TOKEN}"}
    return {}

def handle_response(response):
    if response.status_code >= 400:
        msg = "Unknown Error"
        try:
            msg = response.json().get("detail", "Error")
        except:
            msg = response.text
        raise APIError(msg, response.status_code)
    try:
        return response.json()
    except:
        return response.text

def login(username, password):
    global TOKEN
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
    data = handle_response(res)
    TOKEN = data["access_token"]
    return TOKEN

def change_password(new_password):
    res = requests.post(f"{BASE_URL}/auth/change-password", params={"new_password": new_password}, headers=get_headers())
    return handle_response(res)

def get_me():
    res = requests.get(f"{BASE_URL}/auth/me", headers=get_headers())
    return handle_response(res)

# --- Admin API ---
def get_users(): return handle_response(requests.get(f"{BASE_URL}/admin/users", headers=get_headers()))
def create_user(data): return handle_response(requests.post(f"{BASE_URL}/admin/users", json=data, headers=get_headers()))
def get_employees(): return handle_response(requests.get(f"{BASE_URL}/admin/employees", headers=get_headers()))
def assign_manager(emp_id, manager_id): return handle_response(requests.put(f"{BASE_URL}/admin/employees/{emp_id}/manager", params={"manager_id": manager_id}, headers=get_headers()))
def create_employee(data): return handle_response(requests.post(f"{BASE_URL}/admin/employees", json=data, headers=get_headers()))
def update_admin_system_config(key, value): return handle_response(requests.put(f"{BASE_URL}/admin/system/config/{key}", json={"value": value}, headers=get_headers()))
def trigger_demo_compliance(day_index): return handle_response(requests.post(f"{BASE_URL}/admin/demo/trigger-compliance", json={"day_index": day_index}, headers=get_headers()))
def get_projects(): return handle_response(requests.get(f"{BASE_URL}/admin/projects", headers=get_headers()))
def get_config(): return handle_response(requests.get(f"{BASE_URL}/admin/config", headers=get_headers()))

# --- Manager API ---
def get_dashboard(): return handle_response(requests.get(f"{BASE_URL}/manager/dashboard", headers=get_headers()))
def get_dashboard_employee(emp_id): return handle_response(requests.get(f"{BASE_URL}/manager/dashboard/{emp_id}", headers=get_headers()))
def get_my_projects(): return handle_response(requests.get(f"{BASE_URL}/manager/projects", headers=get_headers()))
def get_project_details(pid): return handle_response(requests.get(f"{BASE_URL}/manager/projects/{pid}", headers=get_headers()))
def ai_search(pid, req): return handle_response(requests.post(f"{BASE_URL}/manager/ai/search", json={"project_id": pid, "requirement": req}, headers=get_headers()))
def ai_team_search(pid, requirement): return handle_response(requests.post(f"{BASE_URL}/manager/ai/team-search", json={"project_id": pid, "team_requirement": requirement}, headers=get_headers()))
def ai_risk(pid): return handle_response(requests.get(f"{BASE_URL}/manager/ai/risk-summary/{pid}", headers=get_headers()))
def allocate_resource(data): return handle_response(requests.post(f"{BASE_URL}/manager/allocations", json=data, headers=get_headers()))
def get_team_timesheets(week=None): return handle_response(requests.get(f"{BASE_URL}/manager/timesheets", params={"week": week} if week else None, headers=get_headers()))
def unfreeze_employee(eid): return handle_response(requests.post(f"{BASE_URL}/manager/employees/{eid}/unfreeze", headers=get_headers()))

# --- Employee API ---
def submit_timesheet(data): return handle_response(requests.post(f"{BASE_URL}/employee/timesheets", json=data, headers=get_headers()))
def get_my_timesheets(): return handle_response(requests.get(f"{BASE_URL}/employee/timesheets", headers=get_headers()))
def get_my_allocations(): return handle_response(requests.get(f"{BASE_URL}/employee/allocations", headers=get_headers()))
