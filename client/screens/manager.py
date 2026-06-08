import api
import ui

def manager_menu(user):
    while True:
        ui.clear_screen()
        ui.print_welcome(user["full_name"], "MANAGER")
        choice = ui.get_menu_choice([
            "Resource Dashboard",
            "Allocate Resource",
            "My Projects",
            "Timesheets",
            "AI Assistant",
            "Logout"
        ])

        if choice == "1":
            resource_dashboard()
        elif choice == "2":
            allocate_resource()
        elif choice == "3":
            my_projects()
        elif choice == "4":
            view_timesheets()
        elif choice == "5":
            ai_assistant()
        elif choice == "6":
            api.TOKEN = None
            return
        else:
            ui.print_error("Invalid option")
            ui.get_input("Press Enter to continue...")

# ==================== RESOURCE DASHBOARD ====================
def resource_dashboard():
    ui.clear_screen()
    from datetime import datetime
    ui.print_header(f"RESOURCE DASHBOARD — {datetime.now().strftime('%B %Y')}")
    try:
        data = api.get_dashboard()
        bench = data.get("bench", [])
        active = data.get("active", [])

        print(f"ON BENCH  ({len(bench)} employees available)")
        ui.print_separator()
        if bench:
            headers = ["ID", "Name", "Department", "Skills"]
            rows = [[e["id"], e["name"], e["department"], ", ".join(e.get("skills", []))] for e in bench]
            ui.print_table(headers, rows, [6, 18, 14, 30])
        else:
            print("(No employees on bench)")

        print(f"\nACTIVE EMPLOYEES")
        ui.print_separator()
        if active:
            headers = ["ID", "Name", "Alloc %", "Availability"]
            rows = []
            for e in active:
                util = e["current_utilisation"]
                avail = "FULL" if util >= 100 else f"{100 - util}% free"
                rows.append([e["id"], e["name"], f"{util}%", avail])
            ui.print_table(headers, rows, [6, 18, 10, 14])
        else:
            print("(No active employees)")

        over = sum(1 for e in active if e["current_utilisation"] > 100)
        partial = sum(1 for e in active if 0 < e["current_utilisation"] < 100)
        print(f"\nBench: {len(bench)}   |   Over-utilised: {over}   |   Partial: {partial}")

        print("\n[D] Drill into employee details     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "D":
            emp_id = ui.get_input("Enter Employee ID: ")
            if emp_id:
                try:
                    emp = api.get_dashboard_employee(emp_id)
                    print(f"\n── {emp['name']} ─────────────────────────────────")
                    print(f"Department     : {emp['department']}")
                    print(f"Current Status : {emp['status']}")
                    print(f"Profile Skills : {', '.join(emp.get('skills', []))}")
                    
                    print("\nActive Allocations:")
                    if emp.get('allocations'):
                        print("  Project          %     From         To")
                        for a in emp['allocations']:
                            from datetime import datetime
                            try:
                                f_date = datetime.strptime(str(a['from']), '%Y-%m-%d').strftime('%d-%b-%y')
                                t_date = datetime.strptime(str(a['to']), '%Y-%m-%d').strftime('%d-%b-%y')
                            except:
                                f_date = str(a['from'])
                                t_date = str(a['to'])
                            print(f"  {a['project']:<15}  {a['percentage']}%    {f_date:<11}  {t_date}")
                    else:
                        print("  None")
                        
                    print("\nRecent Activity Tags (last 4 weeks):")
                    print(f"  {', '.join(emp.get('recent_tags', []))}")
                    
                    ui.get_input("\n[B] Back > ")
                except api.APIError as e:
                    ui.print_error(e.message)
                    ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== ALLOCATE RESOURCE ====================
def allocate_resource():
    while True:
        ui.clear_screen()
        ui.print_header("ALLOCATE RESOURCE")
        choice = ui.get_menu_choice([
            "Find resource using AI (recommended)",
            "Allocate directly (I already know who I want)",
            "End an existing allocation",
            "Back"
        ])

        if choice == "1":
            ai_allocate()
        elif choice == "2":
            direct_allocate()
        elif choice == "3":
            end_allocation()
        elif choice == "4":
            return

def ai_allocate():
    ui.clear_screen()
    ui.print_header("ALLOCATE RESOURCE")

    print("Step 1 — Select Project")
    try:
        projects = api.get_my_projects()
        if not projects:
            ui.print_error("You have no projects assigned.")
            ui.get_input("Press Enter to continue...")
            return
        for p in projects:
            print(f"  {p['id']}. {p['name']}")
        project_id = ui.get_input("\nEnter project ID: ")
        if not project_id:
            return

        print("\nStep 2 — Describe your requirement")
        print("Type what kind of resource you need:")
        requirement = ui.get_input("> ")
        if not requirement:
            return

        print("\nSearching... (AI matching in progress)")
        result = api.ai_search(int(project_id), requirement)
        ui.print_separator()
        print("AI-MATCHED RESULTS")
        ui.print_separator()
        print(result.get("results", "No results."))
        print("\nNote: Suggestions are AI-generated. Verify before confirming.")
        ui.print_separator()

        emp_id = ui.get_input("\nSelect employee (enter #, or 0 to search again): ")
        if emp_id and emp_id != "0":
            proj = next((p for p in projects if str(p['id']) == str(project_id)), None)
            project_name = proj['name'] if proj else f"Project {project_id}"
            perform_allocation(project_id, project_name, emp_id)
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def direct_allocate():
    ui.clear_screen()
    ui.print_header("DIRECT ALLOCATION")
    try:
        projects = api.get_my_projects()
        if not projects:
            ui.print_error("You have no projects assigned.")
            ui.get_input("Press Enter to continue...")
            return
        for p in projects:
            print(f"  {p['id']}. {p['name']}")
        project_id = ui.get_input("\nSelect Project ID : ")
        emp_id = ui.get_input("Enter Employee ID : ")

        if project_id and emp_id:
            proj = next((p for p in projects if str(p['id']) == str(project_id)), None)
            project_name = proj['name'] if proj else f"Project {project_id}"
            perform_allocation(project_id, project_name, emp_id)
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def perform_allocation(project_id, project_name, emp_id):
    try:
        dash = api.get_resource_dashboard()
        all_emps = dash.get("bench", []) + dash.get("active", [])
        emp = next((e for e in all_emps if str(e["id"]) == str(emp_id)), None)
        emp_name = emp['name'] if emp else f"Employee {emp_id}"
        current_util = emp['current_utilisation'] if emp else 0
        
        print(f"\n── {emp_name} ─────────────────────────────────")
        util_str = f"Current Utilisation: {current_util}%"
        if current_util == 0:
            util_str += "   (fully on bench)"
        print(util_str)
    except:
        emp_name = f"Employee {emp_id}"
        current_util = 0
        print(f"\n── {emp_name} ─────────────────────────────────")

    print("\nSet Allocation:")
    util = ui.get_input("  Utilisation %   : ")
    from_date = ui.get_input("  From Date       : (YYYY-MM-DD) ")
    to_date = ui.get_input("  To Date         : (YYYY-MM-DD) ")

    if not all([util, from_date, to_date]):
        ui.print_error("All fields required.")
        return

    util_val = int(util.replace("%", "").strip())
    print("\nValidating...")
    print(f"  {emp_name} total in this period: {current_util}% + {util_val}% = {current_util + util_val}%   ✓ Valid")
    print(f"\n[C] Confirm Allocation     [B] Back")
    choice = ui.get_input("> ").upper()
    if choice == "C":
        try:
            result = api.allocate_resource({
                "employee_id": int(emp_id),
                "project_id": int(project_id),
                "utilisation_percentage": util_val,
                "from_date": from_date,
                "to_date": to_date
            })
            ui.print_success(f"Allocation saved. {emp_name} → {project_name} ({util_val}%, {from_date} to {to_date}) ✓")
        except api.APIError as e:
            ui.print_error(e.message)

def end_allocation():
    ui.clear_screen()
    ui.print_header("END ALLOCATION")
    try:
        projects = api.get_my_projects()
        if not projects:
            ui.print_error("You have no projects.")
            ui.get_input("Press Enter to continue...")
            return
        for p in projects:
            print(f"  {p['id']}. {p['name']}")
        project_id = ui.get_input("\nSelect Project ID: ")
        if not project_id:
            return

        details = api.get_project_details(int(project_id))
        proj_name = details.get("name", f"Project {project_id}")
        allocs = details.get("allocations", [])

        if not allocs:
            print("No active allocations on this project.")
            ui.get_input("Press Enter to continue...")
            return

        print(f"\nActive Allocations on this project:")
        print("  #   Employee        %     From         To")
        for i, a in enumerate(allocs):
            from datetime import datetime
            try:
                f_date = datetime.strptime(str(a['from']), '%Y-%m-%d').strftime('%d-%b-%y')
                t_date = datetime.strptime(str(a['to']), '%Y-%m-%d').strftime('%d-%b-%y')
            except:
                f_date = str(a['from'])
                t_date = str(a['to'])
            print(f"  {i+1}.  {a['employee']:<13}  {a['percentage']}%    {f_date:<11}  {t_date}")
        ui.print_separator()

        sel = ui.get_input("\nSelect allocation to end (#): ")
        if sel and sel.isdigit() and 1 <= int(sel) <= len(allocs):
            alloc = allocs[int(sel) - 1]
            print(f"\nEnd {alloc['employee']}'s allocation on {proj_name}?")
            from datetime import datetime
            today_str = datetime.now().strftime("%d-%b-%Y")
            print(f"Set end date to today ({today_str})?")
            print("\n[Y] Yes, End Now    [B] Back")
            choice = ui.get_input("> ").upper()
            if choice == "Y":
                import requests as req
                api.handle_response(
                    req.put(f"{api.BASE_URL}/manager/allocations/{alloc['id']}/end", headers=api.get_headers())
                )
                ui.print_success(f"Allocation ended. {alloc['employee']} freed from {proj_name} as of {today_str}.")
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== MY PROJECTS ====================
def my_projects():
    ui.clear_screen()
    ui.print_header("MY PROJECTS")
    try:
        projects = api.get_my_projects()
        if not projects:
            print("No projects assigned to you.")
            ui.get_input("\n[B] Back > ")
            return

        headers = ["#", "Project", "End Date", "Health"]
        rows = [[i+1, p["name"], p["end_date"], p.get("health", p["status"])] for i, p in enumerate(projects)]
        ui.print_table(headers, rows, [5, 18, 12, 16])

        sel = ui.get_input("\nSelect project number to view details (or B to go back): ")
        if sel and sel.isdigit() and 1 <= int(sel) <= len(projects):
            proj = projects[int(sel) - 1]
            show_project_detail(proj["id"])
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def show_project_detail(project_id):
    ui.clear_screen()
    try:
        details = api.get_project_details(project_id)
        print(f"── {details['name']} ───────────────────────────────")
        print(f"Health Status : {details.get('health', details['status'])}")

        print("\nRisk Flags:")
        flags = details.get("risk_flags", [])
        if flags:
            for r in flags:
                print(f"  {r}")
        else:
            print("  ✓ No specific risk flags found.")

        print("\nMilestones:")
        if details.get("milestones"):
            headers = ["#", "Title", "Due Date", "Status"]
            rows = [[i+1, m["title"], m["due_date"], m["status"]] for i, m in enumerate(details["milestones"])]
            ui.print_table(headers, rows, [5, 20, 12, 16])
        else:
            print("  (No milestones)")

        print("\nAllocated Resources:")
        if details.get("allocations"):
            print("  Name           %      From         To")
            for a in details["allocations"]:
                from datetime import datetime
                try:
                    f_date = datetime.strptime(str(a['from']), '%Y-%m-%d').strftime('%d-%b-%y')
                    t_date = datetime.strptime(str(a['to']), '%Y-%m-%d').strftime('%d-%b-%y')
                except:
                    f_date = str(a['from'])
                    t_date = str(a['to'])
                print(f"  {a['employee']:<13}  {a['percentage']}%    {f_date:<11}  {t_date}")
        else:
            print("  (No allocations)")

        ui.print_separator()
        print("[A] Get AI Risk Summary     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "A":
            print("\nGenerating AI summary...")
            result = api.ai_risk(project_id)
            print(f"\n── AI Risk Summary — {details['name']} ────────────\n")
            print(result.get("summary", "No summary available."))
            print("\n  Note: This summary is AI-generated from milestone and timesheet data.")
            ui.get_input("\n[B] Back > ")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== TIMESHEETS ====================
def view_timesheets():
    ui.clear_screen()
    ui.print_header("TIMESHEETS — MY TEAM")
    try:
        print("Filter by week (YYYY-MM-DD) or press Enter for current week:")
        week = ui.get_input("Week: ")
        
        if not week:
            from datetime import date, timedelta
            today = date.today()
            week = (today - timedelta(days=today.weekday())).isoformat()
            print(week)

        timesheets = api.get_team_timesheets(week)

        if not timesheets:
            print("No timesheets found.")
            ui.get_input("Press Enter to continue...")
            return

        ui.print_separator()
        headers = ["Employee", "Project", "Hrs", "Status"]
        rows = [[t["employee"], t["project"], t["hours"], t["status"]] for t in timesheets]
        ui.print_table(headers, rows, [18, 18, 6, 16])
        ui.print_separator()
        
        print("\n[V] View employee timesheet detail     [B] Back")
        choice = ui.get_input("> ").upper()
        # [V] is a placeholder for now, just like [B] it goes back since there's no deeper timesheet detail view in the mockup.
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== AI ASSISTANT ====================
def ai_assistant():
    while True:
        ui.clear_screen()
        ui.print_header("AI ASSISTANT")
        choice = ui.get_menu_choice([
            "Skill Match    — Find best employees for a project requirement",
            "Risk Summary   — Get a health analysis for a project",
            "Back"
        ])

        if choice == "1":
            skill_match()
        elif choice == "2":
            risk_summary()
        elif choice == "3":
            return

def skill_match():
    ui.clear_screen()
    print("── Skill Match ────────────────────────────────\n")
    try:
        projects = api.get_my_projects()
        if not projects:
            ui.print_error("No projects found.")
            ui.get_input("Press Enter to continue...")
            return
        for p in projects:
            print(f"  {p['id']}. {p['name']}")
        project_id = ui.get_input("\nSelect project ID: ")
        if not project_id:
            return

        print("\nDescribe your project requirement in plain English:")
        req = ui.get_input("> ")
        if not req:
            return

        print("\nSearching... (calling AI)\n")
        result = api.ai_search(int(project_id), req)
        print("Results:")
        print(result.get("results", "No results."))
        print("\n  Note: These are AI-generated suggestions. Always verify availability")
        print("  and skills with the employee before allocating.")
        print("\n[A] Go to Allocate Resource     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "A":
            allocate_resource()
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

def risk_summary():
    ui.clear_screen()
    print("── Risk Summary ───────────────────────────────\n")
    try:
        projects = api.get_my_projects()
        if not projects:
            ui.print_error("No projects found.")
            ui.get_input("Press Enter to continue...")
            return

        print("Select project:")
        for i, p in enumerate(projects, 1):
            print(f"  {i}.  {p['name']}    {p.get('health', p['status'])}")

        sel = ui.get_input("\nEnter project number: ")
        if sel and sel.isdigit() and 1 <= int(sel) <= len(projects):
            proj = projects[int(sel) - 1]
            print("\nGenerating AI summary...\n")
            result = api.ai_risk(proj["id"])
            print(result.get("summary", "No summary available."))
            print("\n  Note: AI-generated from current milestone and timesheet data.")
        ui.get_input("\n[B] Back > ")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")
