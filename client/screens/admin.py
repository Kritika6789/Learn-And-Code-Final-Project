import api
import ui
from screens.login import password_is_strong

def admin_menu(user):
    while True:
        ui.clear_screen()
        ui.print_welcome(user["full_name"], "ADMIN")
        choice = ui.get_menu_choice([
            "Manage Employees",
            "Manage Projects",
            "View All Allocations",
            "Manage Users",
            "System Configuration",
            "Logout"
        ])

        if choice == "1":
            manage_employees()
        elif choice == "2":
            manage_projects()
        elif choice == "3":
            view_all_allocations()
        elif choice == "4":
            manage_users()
        elif choice == "5":
            system_config()
        elif choice == "6":
            api.TOKEN = None
            return
        else:
            ui.print_error("Invalid option")
            ui.get_input("Press Enter to continue...")

# ==================== MANAGE EMPLOYEES ====================
def manage_employees():
    while True:
        ui.clear_screen()
        ui.print_header("MANAGE EMPLOYEES")
        choice = ui.get_menu_choice([
            "View All Employees",
            "Update Employee",
            "Deactivate Employee",
            "Manage Employee Skills",
            "Assign Manager",
            "Back"
        ])

        if choice == "1":
            view_all_employees()
        elif choice == "2":
            update_employee()
        elif choice == "3":
            deactivate_employee()
        elif choice == "4":
            manage_skills()
        elif choice == "5":
            assign_manager()
        elif choice == "6":
            return
        else:
            ui.print_error("Invalid option")
            ui.get_input("Press Enter to continue...")

def assign_manager():
    ui.clear_screen()
    ui.print_header("ASSIGN MANAGER")

    emp_id = ui.get_input("Employee User ID : ")
    if not emp_id:
        return
    manager_id = ui.get_input("Manager User ID  : ")
    
    print("\n" + "─"*46)
    print("[S] Save     [B] Back")
    choice = ui.get_input("> ").upper()
    if choice == "S":
        try:
            res = api.assign_manager(emp_id, manager_id)
            ui.print_success(res.get("message", "Manager assigned successfully."))
            ui.get_input("Press Enter to continue...")
        except api.APIError as e:
            ui.print_error(e.message)
            ui.get_input("Press Enter to continue...")

def add_employee():
    ui.clear_screen()
    ui.print_header("ADD EMPLOYEE")

    user_id = ui.get_input("User ID      : (from Manage Users → View All Users) ")
    if not user_id:
        return
    full_name = ui.get_input("Full Name    : ")
    email = ui.get_input("Email        : ")
    department = ui.get_input("Department   : ")
    designation = ui.get_input("Designation  : ")

    if not all([user_id, full_name, email, department, designation]):
        ui.print_error("All fields are mandatory")
        ui.get_input("Press Enter to continue...")
        return

    ui.print_separator()
    print("[S] Save     [B] Back")
    choice = ui.get_input("> ").upper()
    if choice == "S":
        try:
            result = api.create_employee({
                "user_id": int(user_id),
                "full_name": full_name,
                "email": email,
                "department": department,
                "designation": designation
            })
            ui.print_success(f"Employee '{full_name}' added with ID {result['id']}")
        except api.APIError as e:
            ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def view_all_employees():
    ui.clear_screen()
    ui.print_header("ALL EMPLOYEES")
    try:
        employees = api.get_employees()
        if not employees:
            print("No employees found.")
        else:
            headers = ["ID", "Name", "Department", "Status"]
            rows = [[e["id"], e["full_name"], e["department"], e["status"]] for e in employees]
            ui.print_table(headers, rows, [6, 18, 14, 12])

            allocated = sum(1 for e in employees if e["status"] == "ALLOCATED")
            bench = len(employees) - allocated
            print(f"\nTotal: {len(employees)}   |   Allocated: {allocated}   |   Bench: {bench}")

        print("\n[F] Filter by Status / Department     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "F":
            filter_val = ui.get_input("Enter status (BENCH/ALLOCATED) or department name: ").upper()
            filtered = [e for e in employees if e["status"] == filter_val or e["department"].upper() == filter_val]
            if filtered:
                rows = [[e["id"], e["full_name"], e["department"], e["status"]] for e in filtered]
                ui.print_table(headers, rows, [6, 18, 14, 12])
            else:
                print("No matching employees.")
            ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def update_employee():
    ui.clear_screen()
    ui.print_header("UPDATE EMPLOYEE")
    print("(This feature allows updating department and designation)")
    emp_id = ui.get_input("Enter Employee ID: ")
    if not emp_id:
        return
    try:
        employees = api.get_employees()
        emp = next((e for e in employees if str(e["id"]) == emp_id), None)
        if not emp:
            ui.print_error("Employee not found")
            ui.get_input("Press Enter to continue...")
            return
        print(f"\n── {emp['full_name']} ─────────────────────────────────")
        print(f"Department  : {emp['department']}")
        print(f"Designation : {emp['designation']}")
        print(f"Status      : {emp['status']}")
        print("\n(Update functionality via direct API)")
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def deactivate_employee():
    ui.clear_screen()
    ui.print_header("DEACTIVATE EMPLOYEE")
    emp_id = ui.get_input("Enter Employee ID: ")
    if not emp_id:
        return
    try:
        employees = api.get_employees()
        emp = next((e for e in employees if str(e["id"]) == emp_id), None)
        if not emp:
            ui.print_error("Employee not found")
            ui.get_input("Press Enter to continue...")
            return

        print(f"\n── {emp['full_name']} ─────────────────────────────────")
        print(f"Department : {emp['department']}")
        print(f"Status     : {emp['status']}")

        print(f"\nAre you sure you want to deactivate {emp['full_name']}?")
        print("This will: set is_active = false, end all active allocations today,")
        print("and block their login account.")
        print()
        print("[Y] Yes, Deactivate     [B] Cancel")
        choice = ui.get_input("> ").upper()
        if choice == "Y":
            result = api.handle_response(
                __import__('requests').put(f"{api.BASE_URL}/admin/employees/{emp_id}/deactivate", headers=api.get_headers())
            )
            ui.print_success("Employee deactivated.")
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def manage_skills():
    ui.clear_screen()
    ui.print_header("MANAGE SKILLS")
    emp_id = ui.get_input("Enter Employee ID: ")
    if not emp_id:
        return

    while True:
        try:
            employees = api.get_employees()
            emp = next((e for e in employees if str(e["id"]) == emp_id), None)
            if not emp:
                ui.print_error("Employee not found")
                ui.get_input("Press Enter to continue...")
                return

            skills = api.handle_response(
                __import__('requests').get(f"{api.BASE_URL}/admin/employees/{emp_id}/skills", headers=api.get_headers())
            )

            ui.clear_screen()
            ui.print_header("MANAGE SKILLS")
            print(f"── {emp['full_name']} ─────────────────────────────────")
            print("Current Skills:")
            if skills:
                for i, s in enumerate(skills, 1):
                    print(f"  {i}.  {s['name']:<20}{s['proficiency_level']}")
            else:
                print("  (No skills assigned)")
            ui.print_separator()

            choice = ui.get_menu_choice([
                "Add Skill",
                "Update Proficiency Level",
                "Remove Skill",
                "Back"
            ])

            if choice == "1":
                skill_name = ui.get_input("Skill Name        : ")
                if not skill_name:
                    continue
                print("Category          : (1) Backend  (2) Frontend  (3) DevOps  (4) QA  (5) Other")
                cat_choice = ui.get_input("Enter choice      : ")
                categories = {"1": "Backend", "2": "Frontend", "3": "DevOps", "4": "QA", "5": "Other"}
                category = categories.get(cat_choice, "Other")

                print("Proficiency Level : (1) Beginner  (2) Intermediate  (3) Advanced")
                prof_choice = ui.get_input("Enter choice      : ")
                levels = {"1": "Beginner", "2": "Intermediate", "3": "Advanced"}
                proficiency = levels.get(prof_choice, "Beginner")

                result = api.handle_response(
                    __import__('requests').post(
                        f"{api.BASE_URL}/admin/employees/{emp_id}/skills",
                        json={"name": skill_name, "category": category, "proficiency_level": proficiency},
                        headers=api.get_headers()
                    )
                )
                ui.print_success("Skill added.")
            elif choice == "4":
                return
        except api.APIError as e:
            ui.print_error(e.message)
            ui.get_input("Press Enter to continue...")
            return

# ==================== MANAGE PROJECTS ====================
def manage_projects():
    while True:
        ui.clear_screen()
        ui.print_header("MANAGE PROJECTS")
        choice = ui.get_menu_choice([
            "Create Project",
            "View All Projects",
            "Update Project Details",
            "Manage Milestones",
            "Back"
        ])

        if choice == "1":
            create_project()
        elif choice == "2":
            view_all_projects()
        elif choice == "3":
            print("(Update project details via API)")
            ui.get_input("Press Enter to continue...")
        elif choice == "4":
            manage_milestones()
        elif choice == "5":
            return

def create_project():
    ui.clear_screen()
    ui.print_header("CREATE PROJECT")

    name = ui.get_input("Project Name  : ")
    description = ui.get_input("Description   : ")
    start_date = ui.get_input("Start Date    : (YYYY-MM-DD) ")
    end_date = ui.get_input("End Date      : (YYYY-MM-DD) ")
    print("Status        : (1) PLANNED   (2) ACTIVE   (3) ON_HOLD")
    status_choice = ui.get_input("Enter choice  : ")
    statuses = {"1": "PLANNED", "2": "ACTIVE", "3": "ON_HOLD"}
    status = statuses.get(status_choice, "PLANNED")
    manager_id = ui.get_input("Assign Manager: (Enter Manager User ID) ")

    if not all([name, start_date, end_date, manager_id]):
        ui.print_error("Required fields missing")
        ui.get_input("Press Enter to continue...")
        return

    ui.print_separator()
    print("[S] Save     [B] Back")
    choice = ui.get_input("> ").upper()
    if choice == "S":
        try:
            result = api.handle_response(
                __import__('requests').post(
                    f"{api.BASE_URL}/admin/projects",
                    json={
                        "name": name, "description": description,
                        "start_date": start_date, "end_date": end_date,
                        "status": status, "manager_id": int(manager_id)
                    },
                    headers=api.get_headers()
                )
            )
            ui.print_success(f"Project '{name}' created with ID {result['id']}")
        except api.APIError as e:
            ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def view_all_projects():
    ui.clear_screen()
    ui.print_header("ALL PROJECTS")
    try:
        projects = api.get_projects()
        if not projects:
            print("No projects found.")
        else:
            headers = ["ID", "Name", "Manager ID", "End Date", "Status"]
            rows = [[p["id"], p["name"], p["manager_id"], p["end_date"], p["status"]] for p in projects]
            ui.print_table(headers, rows, [6, 18, 12, 12, 10])
    except api.APIError as e:
        ui.print_error(e.message)
    ui.get_input("\n[B] Back > ")

def manage_milestones():
    ui.clear_screen()
    ui.print_header("MILESTONES")
    project_id = ui.get_input("Enter Project ID: ")
    if not project_id:
        return

    while True:
        try:
            projects = api.get_projects()
            proj = next((p for p in projects if str(p["id"]) == project_id), None)
            if not proj:
                ui.print_error("Project not found")
                ui.get_input("Press Enter to continue...")
                return

            milestones = api.handle_response(
                __import__('requests').get(f"{api.BASE_URL}/manager/projects/{project_id}", headers=api.get_headers())
            ).get("milestones", [])

            ui.clear_screen()
            ui.print_header("MILESTONES")
            print(f"── {proj['name']} ───────────────────────────────")
            headers = ["#", "Title", "Due Date", "Status"]
            rows = [[i+1, m["title"], m["due_date"], m["status"]] for i, m in enumerate(milestones)]
            ui.print_table(headers, rows, [5, 20, 12, 14])

            choice = ui.get_menu_choice([
                "Add Milestone",
                "Update Milestone Status",
                "Back"
            ])

            if choice == "1":
                title = ui.get_input("Title    : ")
                due_date = ui.get_input("Due Date : (YYYY-MM-DD) ")
                print("Status   : (1) NOT_STARTED  (2) IN_PROGRESS  (3) DONE")
                st = ui.get_input("Enter choice: ")
                ms_statuses = {"1": "NOT_STARTED", "2": "IN_PROGRESS", "3": "DONE"}
                ms_status = ms_statuses.get(st, "NOT_STARTED")

                api.handle_response(
                    __import__('requests').post(
                        f"{api.BASE_URL}/admin/projects/{project_id}/milestones",
                        json={"title": title, "due_date": due_date, "status": ms_status},
                        headers=api.get_headers()
                    )
                )
                ui.print_success("Milestone added.")
                ui.get_input("Press Enter to continue...")
            elif choice == "3":
                return
        except api.APIError as e:
            ui.print_error(e.message)
            ui.get_input("Press Enter to continue...")
            return

# ==================== VIEW ALL ALLOCATIONS ====================
def view_all_allocations():
    ui.clear_screen()
    ui.print_header("ALL ALLOCATIONS")
    try:
        allocs = api.handle_response(
            __import__('requests').get(f"{api.BASE_URL}/admin/allocations", headers=api.get_headers())
        )
        if not allocs:
            print("No active allocations found.")
        else:
            headers = ["Emp ID", "Project ID", "%", "From", "To"]
            rows = [[a["employee_id"], a["project_id"], f"{a['utilisation_percentage']}%", a["from_date"], a["to_date"]] for a in allocs]
            ui.print_table(headers, rows, [8, 12, 6, 12, 12])
            print(f"\nTotal Active Allocations: {len(allocs)}")
    except api.APIError as e:
        ui.print_error(e.message)

    print("\n[F] Filter by Employee / Project     [B] Back")
    ui.get_input("> ")

# ==================== MANAGE USERS ====================
def manage_users():
    while True:
        ui.clear_screen()
        ui.print_header("MANAGE USERS")
        choice = ui.get_menu_choice([
            "Create User Account",
            "View All Users",
            "Reset User Password",
            "Deactivate User",
            "Back"
        ])

        if choice == "1":
            create_user()
        elif choice == "2":
            view_all_users()
        elif choice == "3":
            reset_password()
        elif choice == "4":
            deactivate_user()
        elif choice == "5":
            return

def create_user():
    ui.clear_screen()
    ui.print_header("CREATE USER ACCOUNT")

    full_name = ui.get_input("Full Name         : ")
    email = ui.get_input("Email             : ")
    username = ui.get_input("Username          : ")
    temp_pw = ui.get_input("Temporary Password: ")
    print("Role              : (1) Admin  (2) Manager  (3) Employee")
    role_choice = ui.get_input("Enter choice      : ")
    roles = {"1": "ADMIN", "2": "MANAGER", "3": "EMPLOYEE"}
    role = roles.get(role_choice, "EMPLOYEE")

    if not all([full_name, email, username, temp_pw]):
        ui.print_error("All fields are mandatory")
        ui.get_input("Press Enter to continue...")
        return

    valid, msg = password_is_strong(temp_pw)
    if not valid:
        ui.print_error(msg)
        ui.get_input("Press Enter to continue...")
        return

    ui.print_separator()
    print("[S] Save     [B] Back")
    choice = ui.get_input("> ").upper()
    if choice == "S":
        try:
            result = api.create_user({
                "full_name": full_name,
                "email": email,
                "username": username,
                "password": temp_pw,
                "role": role
            })
            ui.print_success(f"Account created. User must change password on first login.")
        except api.APIError as e:
            ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def view_all_users():
    ui.clear_screen()
    ui.print_header("ALL USERS")
    try:
        users = api.get_users()
        headers = ["ID", "Username", "Role", "Status"]
        rows = [[u["id"], u["username"], u["role"], "Active" if u["is_active"] else "Inactive"] for u in users]
        ui.print_table(headers, rows, [6, 18, 12, 10])

        active = sum(1 for u in users if u["is_active"])
        inactive = len(users) - active
        print(f"\nTotal: {len(users)}   |   Active: {active}   |   Inactive: {inactive}")

        print("\n[R] Reactivate a user     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "R":
            uid = ui.get_input("Enter User ID to reactivate: ")
            if uid:
                user = next((u for u in users if str(u["id"]) == uid), None)
                if user and not user["is_active"]:
                    print(f"\nUser: {user['full_name']} ({user['role']}) — currently Inactive")
                    if ui.confirm("Reactivate this account?"):
                        api.handle_response(
                            __import__('requests').put(f"{api.BASE_URL}/admin/users/{uid}/reactivate", headers=api.get_headers())
                        )
                        ui.print_success(f"Account reactivated. {user['full_name']} can now log in.")
                        print("Note: Previous allocations are NOT restored.")
                else:
                    ui.print_error("User not found or already active.")
                ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def reset_password():
    ui.clear_screen()
    ui.print_header("RESET USER PASSWORD")
    identifier = ui.get_input("Enter Username or User ID: ")
    if not identifier:
        return
    try:
        users = api.get_users()
        user = next((u for u in users if str(u["id"]) == identifier or u["username"] == identifier), None)
        if not user:
            ui.print_error("User not found")
            ui.get_input("Press Enter to continue...")
            return

        print(f"\nUser found: {user['full_name']} ({user['role']})")
        temp_pw = ui.get_input("\nNew Temporary Password: ")
        if not temp_pw:
            return

        valid, msg = password_is_strong(temp_pw)
        if not valid:
            ui.print_error(msg)
            ui.get_input("Press Enter to continue...")
            return

        ui.print_separator()
        print("[S] Save     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "S":
            api.handle_response(
                __import__('requests').put(
                    f"{api.BASE_URL}/admin/users/{user['id']}/reset-password",
                    params={"temp_password": temp_pw},
                    headers=api.get_headers()
                )
            )
            ui.print_success("Password reset. User will be prompted to change it on next login.")
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def deactivate_user():
    ui.clear_screen()
    ui.print_header("DEACTIVATE USER")
    identifier = ui.get_input("Enter Username or User ID: ")
    if not identifier:
        return
    try:
        users = api.get_users()
        user = next((u for u in users if str(u["id"]) == identifier or u["username"] == identifier), None)
        if not user:
            ui.print_error("User not found")
            ui.get_input("Press Enter to continue...")
            return

        print(f"\nUser found: {user['full_name']} ({user['role']})")
        print(f"Status     : {'Active' if user['is_active'] else 'Inactive'}")
        print("\nAre you sure you want to deactivate this account?")
        print("Deactivated users cannot log in. Their data is preserved.")
        print("\n[Y] Yes, Deactivate     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "Y":
            api.handle_response(
                __import__('requests').put(f"{api.BASE_URL}/admin/users/{user['id']}/deactivate", headers=api.get_headers())
            )
            ui.print_success("User deactivated.")
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== SYSTEM CONFIGURATION ====================
def system_config():
    while True:
        ui.clear_screen()
        ui.print_header("SYSTEM CONFIGURATION")
        try:
            config = api.get_config()
            print("Current Settings:")
            llm_key = config.get("LLM_API_KEY", "")
            masked_key = "****************************" if llm_key else "(not set)"
            print(f"  LLM Provider        :  {config.get('LLM_PROVIDER', 'N/A')}")
            print(f"  LLM API Key         :  {masked_key}")
            print(f"  Scheduler Interval  :  {config.get('SCHEDULER_INTERVAL_HOURS', 'N/A')} hours")
            print(f"  Max Weekly Hours    :  {config.get('MAX_WEEKLY_HOURS', 'N/A')}")
            ui.print_separator()

            choice = ui.get_menu_choice([
                "Update LLM API Key",
                "Change LLM Provider  (Gemini / Groq)",
                "Update Scheduler Interval",
                "Update Max Weekly Hours",
                "Back"
            ])

            if choice == "1":
                key = ui.get_input("Enter new LLM API Key: ")
                if key:
                    api.handle_response(
                        __import__('requests').put(f"{api.BASE_URL}/admin/config/LLM_API_KEY", params={"value": key}, headers=api.get_headers())
                    )
                    ui.print_success("API Key updated.")
                    ui.get_input("Press Enter to continue...")
            elif choice == "2":
                provider = ui.get_input("Enter provider (Google Gemini / Groq): ")
                if provider:
                    api.handle_response(
                        __import__('requests').put(f"{api.BASE_URL}/admin/config/LLM_PROVIDER", params={"value": provider}, headers=api.get_headers())
                    )
                    ui.print_success("Provider updated.")
                    ui.get_input("Press Enter to continue...")
            elif choice == "3":
                hrs = ui.get_input("Enter new interval (hours): ")
                if hrs:
                    api.handle_response(
                        __import__('requests').put(f"{api.BASE_URL}/admin/config/SCHEDULER_INTERVAL_HOURS", params={"value": hrs}, headers=api.get_headers())
                    )
                    ui.print_success("Scheduler interval updated.")
                    ui.get_input("Press Enter to continue...")
            elif choice == "4":
                max_hrs = ui.get_input("Enter max weekly hours: ")
                if max_hrs:
                    api.handle_response(
                        __import__('requests').put(f"{api.BASE_URL}/admin/config/MAX_WEEKLY_HOURS", params={"value": max_hrs}, headers=api.get_headers())
                    )
                    ui.print_success("Max weekly hours updated.")
                    ui.get_input("Press Enter to continue...")
            elif choice == "5":
                return
        except api.APIError as e:
            ui.print_error(e.message)
            ui.get_input("Press Enter to continue...")
            return
