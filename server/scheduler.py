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

def start_scheduler():
    scheduler = BackgroundScheduler()
    db = SessionLocal()
    interval = 4
    try:
        config = db.query(models.SystemConfiguration).filter(models.SystemConfiguration.key == "SCHEDULER_INTERVAL_HOURS").first()
        if config:
            interval = int(config.value)
    except Exception:
        pass
    finally:
        db.close()
        
    scheduler.add_job(update_employee_statuses, 'interval', hours=interval)
    scheduler.start()
    logger.info(f"Scheduler started with {interval} hour interval.")
