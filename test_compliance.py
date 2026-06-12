import logging
from datetime import date, timedelta
from server.database import SessionLocal
from server import models
from server.services.email_service import EmailService

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_simulated_check(simulated_today: date):
    print(f"\n=======================================================")
    print(f"SIMULATING DAY: {simulated_today.strftime('%A, %Y-%m-%d')}")
    print(f"=======================================================")
    
    db = SessionLocal()
    try:
        weekday = simulated_today.weekday()
        
        # Only process on Monday(0), Tuesday(1), Wednesday(2)
        if weekday in [0, 1, 2]:
            last_week_start = simulated_today - timedelta(days=weekday + 7)
            last_week_end = last_week_start + timedelta(days=6)
            print(f"Checking for missing timesheets for the week of: {last_week_start} to {last_week_end}")
            
            employees = db.query(models.Employee).all()
            for emp in employees:
                active_allocs = [a for a in emp.allocations if a.from_date <= last_week_end and a.to_date >= last_week_start]
                if not active_allocs:
                    continue
                    
                timesheets = [t for t in emp.timesheets if t.week_start_date == last_week_start]
                if not timesheets:
                    print(f"-> Missing timesheet detected for Employee: {emp.full_name}")
                    emp_email = emp.email
                    manager_email = emp.manager.email if emp.manager else None
                    
                    if weekday == 0:
                        EmailService.send_email(emp_email, "Reminder 1: Missing Timesheet", f"Please submit your timesheet for the week of {last_week_start}.")
                    elif weekday == 1:
                        EmailService.send_email(emp_email, "Reminder 2: Missing Timesheet", f"URGENT: Please submit your timesheet for the week of {last_week_start}.")
                    elif weekday == 2:
                        if not emp.timesheet_frozen:
                            emp.timesheet_frozen = True
                            EmailService.send_email(emp_email, "Account Frozen: Missing Timesheet", f"Your timesheet creation access is frozen due to missing timesheets for the week of {last_week_start}.")
                            if manager_email:
                                EmailService.send_email(manager_email, "Team Member Frozen", f"Employee {emp.full_name} has been frozen from submitting timesheets.")
            db.commit()
        else:
            print("Today is not Monday, Tuesday, or Wednesday. Skipping check.")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure Aditi (ID 7) has NO timesheet submitted for last week
    db = SessionLocal()
    # Unfreeze Aditi just in case
    aditi = db.query(models.Employee).filter(models.Employee.id == 7).first()
    if aditi:
        aditi.timesheet_frozen = False
        db.commit()
    db.close()

    # Simulate Monday (Reminder 1)
    # Let's assume today is June 15th, 2026 (Monday)
    simulated_monday = date(2026, 6, 15)
    run_simulated_check(simulated_monday)
    
    # Simulate Tuesday (Reminder 2)
    simulated_tuesday = date(2026, 6, 16)
    run_simulated_check(simulated_tuesday)
    
    # Simulate Wednesday (Freeze and Notify)
    simulated_wednesday = date(2026, 6, 17)
    run_simulated_check(simulated_wednesday)
