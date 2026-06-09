import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.scheduler import update_employee_statuses

print("Starting manual execution of background scheduler sweep...")
update_employee_statuses()
print("Scheduler sweep completed successfully!")
