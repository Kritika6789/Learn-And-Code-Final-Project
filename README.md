# Project Resource Management (PRM) Tool

A comprehensive, full-stack enterprise application designed to streamline internal project allocation, resource management, and team timesheet tracking.

Built with Python, FastAPI, and an interactive Rich-powered CLI, this tool provides real-time allocation visibility, automated background health checks, and AI-powered skill matching to ensure the right people are assigned to the right projects.

---

## 🌟 Core Features

### 👑 Admin Management
- **User & Employee Control:** Provision new user accounts, onboard employees, and configure skill matrix profiles.
- **Project Oversight:** Create projects, set budgets/story points, and define detailed milestones.
- **System Settings:** Dynamically configure maximum utilization hours and AI provider API keys via a database-driven settings manager (no `.env` restarts required).

### 👔 Manager Workspace
- **Resource Allocation:** Assign employees to projects with specific utilization percentages (up to a globally configured cap).
- **AI Skill Matching (Gemini integration):** Automatically scan the organizational roster to find the best employee for a specific project based on required skills and current availability.
- **AI Risk Summaries:** Generate on-the-fly AI reports analyzing project health, milestone statuses, and timesheet compliance to predict project risks.
- **Team Timesheet Tracking:** View aggregate team timesheets week-over-week. Automatically flags "MISSED" timesheets for allocated employees who failed to log their hours.

### 👩‍💻 Employee Portal
- **Timesheet Submissions:** Log precise working hours and activity tags against allocated projects.
- **Allocation History:** View personal assignment history and upcoming project milestones.
- **Strict Validations:** Enforces submission deadlines (Mondays only) and maximum workload caps.

---

## 🏗️ Architecture & Tech Stack

- **Backend Framework:** FastAPI
- **Database ORM:** SQLAlchemy (SQLite backend)
- **Frontend / Client:** Command Line Interface built with the `rich` library.
- **Authentication:** JWT (JSON Web Tokens) with Bcrypt hashing.
- **Background Tasks:** APScheduler (Automatically transitions employee bench status and flags active projects based on dates).
- **AI Integration:** Google Generative AI (Gemini) SDK.
- **Testing:** Pytest with fully isolated database overriding.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd Learn-And-Code-Final-Project
   ```

2. **Set up a Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database and Start Server**
   Ensure you are in the root directory and start the FastAPI server:
   ```bash
   python -m server.main
   ```

5. **Start the Interactive CLI**
   In a separate terminal (with the virtual environment activated):
   ```bash
   python -m client.app
   ```

---

## 🧪 Running Tests

The test suite provides comprehensive coverage across the Admin, Manager, and Employee API routes, including mocked AI responses.
```bash
$env:PYTHONPATH="."
pytest tests/ -v
```

---

## 📚 Technical Requirements & Engineering Practices

This project rigorously adheres to modern Software Engineering standards:

### 1. SOLID Principles
1. **Single Responsibility Principle (SRP):**
   - `server/auth.py` is solely responsible for password hashing and validation. It does not handle database connections or routing.
2. **Open/Closed Principle (OCP):**
   - `server/services/ai_matcher.py` defines the `IAIMatcher` interface. We implemented `GeminiMatchingStrategy`. If we want to add OpenAI support later, we can simply add an `OpenAIMatchingStrategy` class without modifying the core matching logic.
3. **Liskov Substitution Principle (LSP):**
   - `BaseRepository` (`server/repositories/base.py`) defines standard database operations. `EmployeeRepository` and `ProjectRepository` extend it and can be substituted anywhere a `BaseRepository` is expected without altering correctness.
4. **Interface Segregation Principle (ISP):**
   - In `server/repositories/base.py`, the `IRepository` interface exposes only the essential CRUD methods, ensuring services that only need to read data don't depend on complex monolithic classes that handle deletions.
5. **Dependency Inversion Principle (DIP):**
   - In `server/routers/manager.py`, the router does not depend on direct hardcoded database query strings. Instead, it depends on the `EmployeeRepository` abstraction to fetch employees.

### 2. Design Patterns
1. **Repository Pattern:**
   - Abstracted the database logic away from the FastAPI routers. Instead of polluting `manager.py` with SQLAlchemy queries, it uses `EmployeeRepository(db).get_all()`.
2. **Strategy Pattern:**
   - Used for the AI Skill Matching feature. `GeminiMatchingStrategy` encapsulates the Google Generative AI logic, allowing it to be hot-swapped dynamically.

### 3. Design Principles
1. **Separation of Concerns (SoC):**
   - The application strictly isolates the UI (`client/app.py`), the HTTP/Network layer (`client/api.py`), the Server Routers (`server/routers/`), and the Database Models (`server/models.py`).
2. **Fail Fast:**
   - Demonstrated by Pydantic schemas (`server/schemas.py`) which immediately validate HTTP request payloads and throw `422 Unprocessable Entity` errors before any business logic is executed if a payload is malformed.
3. **DRY (Don't Repeat Yourself):**
   - Common configuration constants (like password lengths and utilization thresholds) are centralized in `server/config.py`. Dynamic secrets (like the API Key) are maintained in the `SystemConfiguration` database table to allow admin modifications without `.env` server restarts.

### 4. Clean Code
- **Meaningful Names:** Functions and variables are highly descriptive (e.g., `validate_password` instead of `chk_pwd`).
- **No Magic Numbers:** Constants like `100` (max utilization) and `8` (min password length) have been extracted to `server/config.py` as `MAX_UTILIZATION_PERCENTAGE` and `MIN_PASSWORD_LENGTH`.
- **No Dead Code:** The codebase has been swept and contains no lingering commented-out functionality or obsolete code blocks.
