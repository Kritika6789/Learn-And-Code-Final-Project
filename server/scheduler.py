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
    db = SessionLocal()
    try:
        projects = db.query(models.Project).all()
        today = date.today()
        
        for proj in projects:
            # Auto-activate planned projects
            if proj.status == "PLANNED" and proj.start_date <= today:
                proj.status = "ACTIVE"
                logger.info(f"Auto-activated project '{proj.name}'")
                
            if proj.status == "ACTIVE":
                overdue_milestones = [m for m in proj.milestones if m.status != "DONE" and m.due_date < today]
                if overdue_milestones:
                    logger.warning(f"PROJECT AT RISK: '{proj.name}' has {len(overdue_milestones)} overdue milestones!")
                
                active_allocs = [a for a in proj.allocations if a.to_date >= today]
                if not active_allocs:
                    logger.warning(f"PROJECT AT RISK: '{proj.name}' has no active resources allocated!")
                    
        db.commit()
    except Exception as e:
        logger.error(f"Scheduler error in flag_project_health: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    db = SessionLocal()
    interval = 24
    try:
        config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "SCHEDULER_INTERVAL_HOURS").first()
        if config:
            interval = int(config.value)
    except Exception:
        pass
    finally:
        db.close()
        
    scheduler.add_job(update_employee_statuses, 'interval', hours=interval)
    scheduler.add_job(flag_project_health, 'interval', hours=interval)
    scheduler.start()
    logger.info(f"Scheduler started with {interval} hour interval.")
