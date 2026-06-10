# PRM Tool (Project Resource Management)

The PRM Tool is an internal platform that enables organization-wide project and resource management.

## Technical Requirements Fulfillment (Grading Rubric 4.3)

This section maps directly to the **4.3 Technical Requirements** rubric to demonstrate where specific engineering practices have been implemented in the codebase.

### 1. SOLID Principles
All five SOLID principles are demonstrable in this codebase:

1. **Single Responsibility Principle (SRP):**
   - *Example:* `server/auth.py` is solely responsible for password hashing and validation. It does not handle database connections or routing.
2. **Open/Closed Principle (OCP):**
   - *Example:* `server/services/ai_matcher.py` defines the `IAIMatcher` interface. We implemented `GeminiMatchingStrategy`. If we want to add OpenAI support later, we can add an `OpenAIMatchingStrategy` without modifying the core matching logic.
3. **Liskov Substitution Principle (LSP):**
   - *Example:* `BaseRepository` (`server/repositories/base.py`) defines standard database operations. `EmployeeRepository` and `ProjectRepository` extend it and can be substituted anywhere a `BaseRepository` is expected without altering correctness.
4. **Interface Segregation Principle (ISP):**
   - *Example:* In `server/repositories/base.py`, the `IRepository` interface exposes only the essential CRUD methods, ensuring services that only need to read don't depend on complex monolithic classes.
5. **Dependency Inversion Principle (DIP):**
   - *Example:* In `server/routers/manager.py`, the router does not depend on direct hardcoded database query strings, but instead depends on the `EmployeeRepository` abstraction to fetch employees.

### 2. Design Patterns
1. **Repository Pattern:**
   - Abstracted the database logic away from the FastAPI routers. Instead of polluting `manager.py` with SQLAlchemy queries, it uses `EmployeeRepository(db).get_all()` (`server/repositories/employee.py`).
2. **Strategy Pattern:**
   - Used for the AI Skill Matching feature. `GeminiMatchingStrategy` encapsulates the Google Generative AI logic, allowing it to be hot-swapped (`server/services/ai_matcher.py`).

### 3. Design Principles
1. **Separation of Concerns (SoC):**
   - The application strictly isolates the UI (the CLI client in `client/app.py`), the HTTP/Network layer (`client/api.py`), the Server Routers (`server/routers/`), and the Database Models (`server/models.py`).
2. **Fail Fast:**
   - Demonstrated by Pydantic schemas (`server/schemas.py`) which immediately validate HTTP request payloads and throw `422 Unprocessable Entity` errors before any business logic is executed if a payload is malformed.
3. **DRY (Don't Repeat Yourself):**
   - Common configuration constants (like password lengths and utilization thresholds) are centralized in `server/config.py`.

### 4. Clean Code
- **Meaningful Names:** Functions and variables are highly descriptive (e.g., `validate_password` instead of `chk_pwd`).
- **No Magic Numbers:** Constants like `100` (max utilization) and `8` (min password length) have been extracted to `server/config.py` as `MAX_UTILIZATION_PERCENTAGE` and `MIN_PASSWORD_LENGTH`.
- **No Dead Code:** The codebase has been swept and contains no lingering commented-out functionality or obsolete code blocks.
