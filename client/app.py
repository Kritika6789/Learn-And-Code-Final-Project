"""
Project & Resource Management Tool — Console Client
====================================================
Entry point for the CLI application.
Connects to the FastAPI backend via REST APIs.
"""

import sys
import os

# Add client directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import api
import ui
from screens.login import login_screen
from screens.admin import admin_menu
from screens.manager import manager_menu
from screens.employee import employee_menu

def main():
    print("Connecting to PRM Tool server...")
    try:
        # Quick health check
        import requests
        res = requests.get("http://127.0.0.1:8000/")
        if res.status_code != 200:
            raise ConnectionError()
    except Exception:
        ui.print_error("Cannot connect to the PRM server at http://127.0.0.1:8000")
        print("Please start the server first with:")
        print("  cd server")
        print("  uvicorn main:app --reload")
        sys.exit(1)

    while True:
        user = login_screen()
        if not user:
            continue

        role = user.get("role", "")

        if role == "ADMIN":
            admin_menu(user)
        elif role == "MANAGER":
            manager_menu(user)
        elif role == "EMPLOYEE":
            employee_menu(user)
        else:
            ui.print_error(f"Unknown role: {role}")
            api.TOKEN = None

if __name__ == "__main__":
    main()
