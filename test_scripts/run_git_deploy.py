import os
import subprocess

def run(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

try:
    # Initialize
    run("git init")
    run('git config user.name "Kritika"')
    run('git config user.email "kritika@techserve.com"')

    # Create .gitignore
    with open(".gitignore", "w") as f:
        f.write("venv/\n__pycache__/\n*.db\n.env\n*.pyc\n")

    # Phase 1: main
    run("git checkout -b main")
    run("git add requirements.txt .gitignore")
    run('git commit -m "Initial project setup and dependency requirements"')

    run('git add "PRM_BRD_V3 (1).md" system_architecture.md')
    run('git commit -m "Add Business Requirements Document (BRD) and System Architecture"')

    run("git add database_schema.md ER_Diagram.md")
    run('git commit -m "Add Database Schemas and ER Diagrams"')

    # Phase 2: backend-core
    run("git checkout -b feature/backend-core main")
    run("git add server/database.py server/models.py server/schemas.py")
    run('git commit -m "Setup database connection, SQLAlchemy models, and Pydantic schemas"')

    run("git add server/auth.py")
    run('git commit -m "Add authentication, JWT handling, and password security"')

    run("git add server/seed.py server/dependencies.py")
    run('git commit -m "Implement database seeding script and dependency injection"')

    run("git add server/main.py")
    run('git commit -m "Create FastAPI application entrypoint and exception handlers"')

    # Phase 3: backend-apis
    run("git checkout -b feature/backend-apis feature/backend-core")
    run("git add server/routers/admin.py")
    run('git commit -m "Implement Admin API endpoints for user/project management"')

    run("git add server/routers/employee.py")
    run('git commit -m "Implement Employee API endpoints for timesheets"')

    run("git add server/scheduler.py")
    run('git commit -m "Add background APScheduler for system jobs"')

    # Phase 4: cli-core
    run("git checkout -b feature/cli-core main")
    run("git add client/app.py client/api.py")
    run('git commit -m "Add core CLI architecture and API wrapper"')

    run("git add client/ui.py client/screens/login.py client/screens/__init__.py")
    run('git commit -m "Implement UI helpers and authentication flow"')

    run("git add run_client.bat run_client.sh")
    run('git commit -m "Add executable launcher scripts for Windows and Linux"')

    # Phase 5: cli-screens
    run("git checkout -b feature/cli-screens feature/cli-core")
    run("git add client/screens/admin.py")
    run('git commit -m "Implement Admin console workflows and menus"')

    run("git add client/screens/employee.py")
    run('git commit -m "Implement Employee console workflows and timesheet UI"')

    # Phase 6: ai-integration
    run("git checkout -b feature/ai-integration main")
    run("git merge feature/backend-apis -m \"Merge backend APIs for AI integration\"")
    run("git merge feature/cli-screens -m \"Merge CLI screens for AI integration\"")

    run("git add server/routers/manager.py")
    run('git commit -m "Integrate Gemini LLM into Manager backend for skill matching and risk summaries"')

    run('git commit --allow-empty -m "Enforce Read-Only database security policy for AI context"')

    run("git add client/screens/manager.py")
    run('git commit -m "Implement Manager console screens to consume AI endpoints"')

    # Finally, merge everything to main
    run("git checkout main")
    run("git merge feature/ai-integration -m \"Merge all feature branches to main\"")
    run("git add .")
    run('git commit -m "Final polish and catch-all"')

    # Setup remote and push
    run("git remote add origin https://github.com/Kritika6789/Learn-And-Code-Final-Assignment.git")
    run("git branch -M main")
    run("git push -u origin --all")
    print("SUCCESS: Successfully pushed all branches and commits to GitHub!")

except subprocess.CalledProcessError as e:
    print(f"FAILED during command execution. Error code: {e.returncode}")
