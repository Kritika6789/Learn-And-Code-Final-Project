from apscheduler.schedulers.background import BackgroundScheduler
from server.database import SessionLocal
from server import models
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_employee_statuses():
    logger.info("Running scheduled task: update_employee_statuses")
    db = SessionLocal()
    try:
        employees = db.query(models.Employee).all()
        today = date.today()
        
        for emp in employees:
            if emp.user and not emp.user.is_active:
                continue
                
            active_allocs = [a for a in emp.allocations if a.from_date <= today <= a.to_date]
            total_util = sum(a.utilisation_percentage for a in active_allocs)
            
            if total_util == 0:
                emp.status = "BENCH"
            else:
                emp.status = "ALLOCATED"
                
        db.commit()
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        db.rollback()
    finally:
        db.close()

def flag_project_health():
    logger.info("Running scheduled task: flag_project_health")
    from server.services.email_service import EmailService
    from server.services.llm_factory import LLMFactory
    from server.routers.manager import get_llm_api_key, get_llm_provider_name, get_llm_host_url
    
    db = SessionLocal()
    try:
        projects = db.query(models.Project).all()
        today = date.today()
        
        for proj in projects:
            if proj.status == "PLANNED" and proj.start_date <= today:
                proj.status = "ACTIVE"
                logger.info(f"Auto-activated project '{proj.name}'")
                
            if proj.status == "ACTIVE":
                overdue_milestones = [m for m in proj.milestones if m.status != "DONE" and m.due_date < today]
                active_allocs = [a for a in proj.allocations if a.to_date >= today]
                
                is_at_risk = bool(overdue_milestones) or not active_allocs
                health_status = "RED" if not active_allocs else ("AMBER" if overdue_milestones else "GREEN")
                
                if health_status in ["AMBER", "RED"]:
                    logger.warning(f"PROJECT AT RISK: '{proj.name}' is {health_status}!")
                    
                    if not proj.at_risk_notified:
                        # 1. AI Risk Summary
                        ai_summary = "AI Error: Could not generate risk summary."
                        api_key = get_llm_api_key(db)
                        provider_name = get_llm_provider_name(db)
                        host_url = get_llm_host_url(db)
                        if api_key and len(api_key) > 5:
                            try:
                                provider = LLMFactory.get_provider(provider_name, host_url=host_url)
                                prompt = f"The project '{proj.name}' is {health_status}. It has {len(overdue_milestones)} overdue milestones and {len(active_allocs)} active allocations. Write a brief, plain-English paragraph explaining why it is at risk and what needs to be done. Do not output markdown, just plain text."
                                ai_summary = provider.generate_content(prompt, api_key)
                            except Exception:
                                pass
                        else:
                            ai_summary = f"Project '{proj.name}' is {health_status}. It has {len(overdue_milestones)} overdue milestones and {len(active_allocs)} active resources. Please review immediately."
                            
                        # 2. Suggested Help (Find BENCH employees)
                        bench_employees = db.query(models.Employee).filter(models.Employee.status == "BENCH").limit(3).all()
                        suggested_help = "None currently available on BENCH."
                        if bench_employees:
                            suggested_help = ", ".join([f"{e.full_name} ({e.designation})" for e in bench_employees])
                            
                        # 3. Send Email
                        if proj.manager and proj.manager.email:
                            milestones_text = ", ".join([m.title for m in proj.milestones[:3]]) or "None"
                            email_body = (
                                f"PROJECT DETAILS:\n"
                                f"Name: {proj.name}\n"
                                f"Manager: {proj.manager.full_name}\n"
                                f"Key Milestones: {milestones_text}\n\n"
                                f"HEALTH STATUS: {health_status}\n\n"
                                f"AI RISK SUMMARY:\n{ai_summary}\n\n"
                                f"SUGGESTED HELP (Available Bench Resources):\n{suggested_help}"
                            )
                            EmailService.send_email(proj.manager.email, f"Project At-Risk Alert: {proj.name}", email_body)
                            
                        proj.at_risk_notified = True
                else:
                    if proj.at_risk_notified:
                        proj.at_risk_notified = False
                        
        db.commit()
    except Exception as e:
        logger.error(f"Scheduler error in flag_project_health: {e}")
        db.rollback()
    finally:
        db.close()

from server.timesheet_scheduler import timesheet_compliance_check
def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    db = SessionLocal()
    interval = 24
    try:
        config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "SCHEDULER_INTERVAL_HOURS").first()
        if config:
            interval = float(config.value)
    except Exception:
        pass
    finally:
        db.close()
        
    scheduler.add_job(update_employee_statuses, 'interval', hours=interval)
    scheduler.add_job(flag_project_health, 'interval', hours=interval)
    scheduler.add_job(timesheet_compliance_check, 'cron', day_of_week='tue,wed,thu', hour=8, minute=0) # Tue=Rem1, Wed=Rem2, Thu=Freeze
    scheduler.start()
    logger.info(f"Scheduler started with {interval} hour interval.")
