# Project & Resource Management (PRM) Tool Documentation

This document outlines the architecture, components, and current status of the Project & Resource Management tool developed so far.

## Architecture Overview

The system follows a classic **Client-Server Architecture**, using modern Python frameworks for both ends.

### 1. Backend Server (FastAPI + SQLAlchemy)
The backend acts as a RESTful API provider, handling data persistence, authentication, authorization, and business logic validation.

*   **Framework**: FastAPI (for high performance and automatic interactive API documentation)
*   **Database**: SQLite (local development database)
*   **ORM**: SQLAlchemy (Python object-relational mapper)
*   **Authentication**: JWT Bearer Tokens (with role-based access control and initial password-change flow)
*   **Background Jobs**: APScheduler (for tracking utilization over time)

#### Backend Structure (`server/`)
*   `models.py`: Defines the SQLAlchemy database tables (User, Employee, Project, Allocation, TimeSheet, SystemConfig, UtilizationRecord).
*   `schemas.py`: Defines Pydantic models for data validation and serialization (request/response models).
*   `database.py`: Database connection and session management.
*   `auth.py`: JWT token generation, verification, and password hashing.
*   `dependencies.py`: Shared dependencies like `get_current_active_user` for authentication across routers.
*   `routers/`: Directory containing endpoints separated by role:
    *   `admin.py`: Endpoints for managing users, employees, and projects.
    *   `manager.py`: Endpoints for allocating resources, viewing team allocations, and AI integration.
    *   `employee.py`: Endpoints for submitting and viewing timesheets.
*   `scheduler.py`: Background tasks (e.g., calculating utilization every 5 minutes).
*   `seed.py`: Script to initialize the database with a default Admin user and system settings.
*   `main.py`: The entry point for the FastAPI application.

### 2. Client Application (Python CLI)
The client provides an interactive text-based interface for users to interact with the backend server via REST APIs.

*   **Architecture**: Synchronous blocking application with a main event loop.
*   **Communication**: Uses the `requests` library to communicate with the FastAPI server.
*   **State Management**: Holds an active JWT token for authorized requests.

#### Client Structure (`client/`)
*   `app.py`: Main entry point containing the initialization logic and role-based routing (the main loop).
*   `api.py`: Core REST client that wraps Python `requests`, handling token injection and standardized error checking.
*   `ui.py`: Utility functions for printing formatted console output (headers, tables, error messages).
*   `screens/`: Directory containing role-specific menus and screens:
    *   `login.py`: Prompts for username/password and handles the force-password-change flow.
    *   `admin.py`: Interactive menus for Admin tasks (creating users, projects).
    *   `manager.py`: Interactive menus for Manager tasks (making allocations, viewing AI suggestions).
    *   `employee.py`: Interactive menus for Employee tasks (logging timesheets).

## Features Implemented

### Administration
*   **System Setup**: Automated database seeding of an initial administrator account.
*   **User Management**: Creating `EMPLOYEE` or `MANAGER` users (generates initial temporary passwords).
*   **Project Management**: Creating new projects with descriptions and statuses.

### Resource Management
*   **Allocations**: Managers can allocate an employee to a project with a specific percentage of their time (e.g., 50%).
*   **Capacity Validation**: System prevents an employee's total allocation from exceeding 100%.
*   **AI Integration**: Managers can invoke an AI assistant (Google Gemini) for recommendations on resource allocation based on current team workloads.

### Time Tracking
*   **Timesheets**: Employees log actual hours worked on their assigned projects, submitting them for specific weeks.
*   **Validation Rules**: 
    *   Can only log time for active, allocated projects.
    *   Cannot log more than 40 hours a week across all projects unless configured otherwise.

## Current State & Next Steps
*   **Completed**: The complete schema, server APIs, and client-side console interfaces are fully written.
*   **In Progress**: Resolving remaining dependencies (e.g., installing `email-validator` for Pydantic email validation).
*   **Next Steps**: 
    1.  Start the FastAPI server.
    2.  Run the client application `python client/app.py` to test the End-to-End flow.
