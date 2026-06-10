import api
import ui
from datetime import date, timedelta

ACTIVITY_TAGS = [
    "Backend API Development",
    "Microservices / Architecture",
    "Database Design & Queries",
    "WebSocket / Real-time Features",
    "Frontend Development",
    "Code Review / Mentoring",
    "Bug Fixing",
    "DevOps / Deployment",
    "Testing & QA",
    "Documentation",
    "Other"
]

def employee_menu(user):
    while True:
        ui.clear_screen()
        ui.print_welcome(user["full_name"], "EMPLOYEE")

        # Check for missed timesheet reminder
        try:
            timesheets = api.get_my_timesheets()
            today = date.today()
            last_monday = today - timedelta(days=today.weekday() + 7)
            last_week_str = str(last_monday)
            submitted_weeks = [t["week_start"] for t in timesheets]
            if last_week_str not in submitted_weeks:
                ui.print_warning(f"Reminder: Timesheet for week {last_monday.strftime('%d-%m-%Y')} has not been submitted.")
        except:
            pass

        ui.print_separator()
        choice = ui.get_menu_choice([
            "Submit Timesheet",
            "View My Timesheets",
            "View My Allocations",
            "Logout"
        ])

        if choice == "1":
            submit_timesheet(user)
        elif choice == "2":
            view_my_timesheets()
        elif choice == "3":
            view_my_allocations()
        elif choice == "4":
            api.TOKEN = None
            return
        else:
            ui.print_error("Invalid option")
            ui.get_input("Press Enter to continue...")

# ==================== SUBMIT TIMESHEET ====================
def submit_timesheet(user):
    ui.clear_screen()
    ui.print_header("SUBMIT TIMESHEET")
    print(f"Employee  : {user['full_name']}")

    while True:
        week_input = ui.get_input("Week Start: Enter date (YYYY-MM-DD) or press Enter for last Monday\n          > ")
        if not week_input:
            today = date.today()
            last_monday = today - timedelta(days=today.weekday())
            if today.weekday() == 0:
                last_monday = today - timedelta(days=7)
            week_input = str(last_monday)
            break
        else:
            try:
                from datetime import datetime
                datetime.strptime(week_input, "%Y-%m-%d")
                break
            except ValueError:
                ui.print_error("Invalid date format. Please use YYYY-MM-DD.")
    
    print(f"\nWeek selected: {week_input}")
    print("Checking your active allocations for this week...")

    try:
        allocations = api.get_my_allocations()
        active_allocs = [a for a in allocations if a.get("status") == "ACTIVE"]

        if not active_allocs:
            ui.print_error("No active allocations found for this week.")
            ui.get_input("Press Enter to continue...")
            return

        entries = []
        total_hours = 0

        for idx, alloc in enumerate(active_allocs, 1):
            ui.print_separator()
            print(f"PROJECT {idx} OF {len(active_allocs)} — {alloc['project']}")
            print(f"  Allocation: {alloc['percentage']}%   |   Expected: {int(alloc['percentage'] * 40 / 100)} hrs max")
            ui.print_separator()

            hours = ui.get_input("Hours worked this week: ")
            if not hours or not hours.isdigit():
                ui.print_error("Invalid hours.")
                continue

            print("\nWhat did you work on? Select activity tags:\n")
            for i, tag in enumerate(ACTIVITY_TAGS, 1):
                print(f"  {i:>2}.  {tag}")

            tag_input = ui.get_input("\nSelect tags (comma-separated): ")
            selected_tags = []
            if tag_input:
                for t in tag_input.split(","):
                    t = t.strip()
                    if t.isdigit() and 1 <= int(t) <= len(ACTIVITY_TAGS):
                        selected_tags.append(ACTIVITY_TAGS[int(t) - 1])
                    else:
                        selected_tags.append(t)

            entries.append({
                "project": alloc["project"],
                "project_id": None,
                "hours": int(hours),
                "tags": selected_tags
            })
            total_hours += int(hours)

        # Summary
        ui.print_separator()
        print("SUMMARY")
        for e in entries:
            print(f"  {e['project']:<20}{e['hours']} hrs    [{', '.join(e['tags'])}]")
        print(f"  {'─' * 40}")
        print(f"  Total           {total_hours} hrs / 40 hrs max   {'✓' if total_hours <= 40 else '✗ EXCEEDS'}")
        ui.print_separator()

        print("[S] Submit Timesheet     [B] Back")
        choice = ui.get_input("> ").upper()
        if choice == "S":
            success_count = 0
            for i, entry in enumerate(entries):
                try:
                    # We need the project_id. Get it from allocations response
                    # For now, submit using the allocation info we have
                    result = api.submit_timesheet({
                        "project_id": active_allocs[i].get("project_id", i + 1),
                        "week_start_date": week_input,
                        "hours_logged": entry["hours"],
                        "activity_tags": ", ".join(entry["tags"])
                    })
                    success_count += 1
                except api.APIError as e:
                    ui.print_error(f"{entry['project']}: {e.message}")
            if success_count > 0:
                ui.print_success(f"Timesheet submitted successfully. Status: SUBMITTED")
        ui.get_input("Press Enter to continue...")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== VIEW MY TIMESHEETS ====================
def view_my_timesheets():
    ui.clear_screen()
    ui.print_header("MY TIMESHEETS")
    try:
        timesheets = api.get_my_timesheets()
        if not timesheets:
            print("No timesheets found.")
        else:
            headers = ["Week Start", "Total Hrs", "Status"]
            rows = [[t["week_start"], f"{t['total_hrs']} hrs", t["status"]] for t in timesheets]
            ui.print_table(headers, rows, [16, 12, 12])

        print("\n[V] View week details     [B] Back")
        ui.get_input("> ")
    except api.APIError as e:
        ui.print_error(e.message)
        ui.get_input("Press Enter to continue...")

# ==================== VIEW MY ALLOCATIONS ====================
def view_my_allocations():
    ui.clear_screen()
    ui.print_header("MY ALLOCATIONS")
    try:
        allocations = api.get_my_allocations()
        if not allocations:
            print("No allocations found.")
        else:
            headers = ["Project", "%", "From", "To", "Status"]
            rows = [[a["project"], f"{a['percentage']}%", a["from"], a["to"], a["status"]] for a in allocations]
            ui.print_table(headers, rows, [18, 6, 12, 12, 12])

            total_util = sum(a["percentage"] for a in allocations if a["status"] == "ACTIVE")
            print(f"\nTotal Utilisation: {total_util}%")
    except api.APIError as e:
        ui.print_error(e.message)

    ui.get_input("\n[B] Back > ")
