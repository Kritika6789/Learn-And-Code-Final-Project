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
    run('git commit -m "chore: initial project setup and dependency requirements"')

    run('git add "PRM_BRD_V3 (1).md" system_architecture.md database_schema.md ER_Diagram.md')
    run('git commit -m "docs: add Business Requirements Document and architecture diagrams"')

    # Push main first
    run("git remote add origin https://github.com/Kritika6789/Learn-And-Code-Final-Project.git")
    run("git push -u origin main")

    # Phase 2: backend-core
    run("git checkout -b feature/backend-core main")
    run("git add server/database.py server/models.py server/schemas.py")
    run('git commit -m "feat(backend): setup SQLite database connection, SQLAlchemy models, and schemas"')

    run("git add server/auth.py")
    run('git commit -m "feat(backend): implement JWT authentication and password hashing"')

    run("git add server/seed.py server/dependencies.py server/main.py")
    run('git commit -m "feat(backend): add database seeding script and FastAPI application entrypoint"')

    # Push backend-core
    run("git push -u origin feature/backend-core")

    # Phase 3: backend-apis
    run("git checkout -b feature/backend-apis feature/backend-core")
    run("git add server/routers/admin.py")
    run('git commit -m "feat(api): implement Admin API endpoints for user and project management"')

    run("git add server/routers/employee.py server/scheduler.py")
    run('git commit -m "feat(api): implement Employee API and background system scheduler"')

    # Push backend-apis
    run("git push -u origin feature/backend-apis")

    # Phase 4: cli-core
    run("git checkout -b feature/cli-core main")
    run("git add client/app.py client/api.py")
    run('git commit -m "feat(cli): add base CLI architecture and REST API wrapper"')

    run("git add client/ui.py client/screens/login.py client/screens/__init__.py")
    run('git commit -m "feat(cli): implement UI helpers and user login workflow"')

    run("git add run_client.bat run_client.sh")
    run('git commit -m "chore: add executable launcher scripts for Windows and Linux"')

    # Push cli-core
    run("git push -u origin feature/cli-core")

    # Phase 5: cli-screens
    run("git checkout -b feature/cli-screens feature/cli-core")
    run("git add client/screens/admin.py")
    run('git commit -m "feat(cli): implement Admin console workflows and menus"')

    run("git add client/screens/employee.py")
    run('git commit -m "feat(cli): implement Employee console workflows and timesheet UI"')

    # Push cli-screens
    run("git push -u origin feature/cli-screens")

    # Phase 6: ai-integration
    run("git checkout -b feature/ai-integration main")
    run("git merge feature/backend-apis -m \"chore: merge backend APIs for AI integration\"")
    run("git merge feature/cli-screens -m \"chore: merge CLI screens for AI integration\"")

    run("git add server/routers/manager.py")
    run('git commit -m "feat(ai): integrate Gemini LLM into Manager backend for skill matching and risk summaries"')

    run("git add client/screens/manager.py")
    run('git commit -m "feat(cli): implement Manager console screens to consume AI endpoints"')

    # Add any remaining stray files (like __init__ files)
    run("git add .")
    run('git commit -m "chore: final polish and catch-all for AI integration branch"')

    # Push ai-integration
    run("git push -u origin feature/ai-integration")
    
    print("SUCCESS: Successfully pushed all feature branches and commits to GitHub!")

except subprocess.CalledProcessError as e:
    print(f"FAILED during command execution. Error code: {e.returncode}")
