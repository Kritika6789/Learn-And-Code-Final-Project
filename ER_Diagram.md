# Database Architecture & Connections

This diagram visualizes how the tables are connected. 
- **PK** indicates a Primary Key (the unique identifier for a row).
- **FK** indicates a Foreign Key (a reference to a Primary Key in another table).
- The lines between the tables indicate the type of relationship (e.g., `||--o{` means "One to Many", `||--o|` means "One to Zero-or-One").

```mermaid
erDiagram
    users ||--o| employees : "1 to 1 (Linked by user_id)"
    users ||--o{ projects : "1 to N (Manager owns projects)"
    
    employees ||--o{ skills : "1 to N"
    employees ||--o{ allocations : "1 to N"
    employees ||--o{ timesheets : "1 to N"
    
    projects ||--o{ milestones : "1 to N"
    projects ||--o{ allocations : "1 to N"
    projects ||--o{ timesheets : "1 to N"

    users {
        Integer id PK
        String username
        String email
        String password_hash
        String role
    }

    employees {
        Integer id PK
        Integer user_id FK "References users.id"
        String full_name
        String status
    }

    skills {
        Integer id PK
        Integer employee_id FK "References employees.id"
        String name
        String proficiency_level
    }

    projects {
        Integer id PK
        Integer manager_id FK "References users.id"
        String name
        String status
    }

    milestones {
        Integer id PK
        Integer project_id FK "References projects.id"
        String title
        String status
    }

    allocations {
        Integer id PK
        Integer employee_id FK "References employees.id"
        Integer project_id FK "References projects.id"
        Integer utilisation_percentage
    }

    timesheets {
        Integer id PK
        Integer employee_id FK "References employees.id"
        Integer project_id FK "References projects.id"
        Integer hours_logged
    }

    system_configuration {
        String key PK
        String value
    }
```
