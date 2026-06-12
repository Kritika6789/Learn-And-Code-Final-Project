import logging
import sys
import os
from datetime import date, timedelta

# Ensure the root project directory is in the Python path when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import SessionLocal
from server import models
from server.services.email_service import EmailService

logger = logging.getLogger(__name__)

def timesheet_compliance_check():
    logger.info("Running scheduled task: timesheet_compliance_check")
    db = SessionLocal()
    try:
        today = date.today()
        # For demo purposes, we will target the CURRENT week's Monday, because your
        # employee dummy data allocations only started this week (June 11th). 
        # If we check the previous week, nobody will have an active allocation!
        last_week_start = today - timedelta(days=today.weekday())
        last_week_end = last_week_start + timedelta(days=6)
        
        employees = db.query(models.Employee).all()
        for emp in employees:
            active_allocs = [a for a in emp.allocations if a.from_date <= last_week_end and a.to_date >= last_week_start]
            if not active_allocs:
                print(f"DEBUG: Skipping {emp.full_name} - No active allocations between {last_week_start} and {last_week_end}")
                continue
                
            timesheets = [t for t in emp.timesheets if t.week_start_date == last_week_start]
            if not timesheets:
                # Employee is missing timesheet, increment state counter
                emp.missing_timesheet_reminders += 1
                print(f"DEBUG: Catching missing timesheet for {emp.full_name}! (Reminder count now at {emp.missing_timesheet_reminders})")
                
                emp_email = emp.email
                manager_email = emp.manager.email if emp.manager else None
                
                if emp.missing_timesheet_reminders == 1:
                    EmailService.send_email(emp_email, "Reminder 1: Missing Timesheet", f"Please submit your timesheet for the week of {last_week_start}.")
                elif emp.missing_timesheet_reminders == 2:
                    EmailService.send_email(emp_email, "Reminder 2: Missing Timesheet", f"URGENT: Please submit your timesheet for the week of {last_week_start}.")
                elif emp.missing_timesheet_reminders >= 3:
                    if not emp.timesheet_frozen:
                        emp.timesheet_frozen = True
                        EmailService.send_email(emp_email, "Account Frozen: Missing Timesheet", f"Your timesheet creation access is frozen due to missing timesheets for the week of {last_week_start}.")
                        if manager_email:
                            EmailService.send_email(manager_email, "Team Member Frozen", f"Employee {emp.full_name} has been frozen from submitting timesheets.")
            else:
                # Employee successfully submitted timesheet, reset state counter
                emp.missing_timesheet_reminders = 0
                print(f"DEBUG: {emp.full_name} has successfully submitted their timesheet. Resetting counter.")
                
        db.commit()
    except Exception as e:
        logger.error(f"Scheduler error in timesheet_compliance_check: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("[MANUAL OVERRIDE] Advancing timesheet state machine for all employees missing timesheets...")
    timesheet_compliance_check()
    print("[MANUAL OVERRIDE] Done. Check logs for generated emails.")


