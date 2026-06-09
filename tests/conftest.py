import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.main import app
from server.database import Base, get_db
from server import models
from server.auth import get_password_hash
from server.dependencies import get_current_active_user

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed required config
    db.add(models.SystemConfiguration(key="MAX_WEEKLY_HOURS", value="40"))
    db.add(models.SystemConfiguration(key="SCHEDULER_INTERVAL_HOURS", value="24"))
    
    # Seed test users
    admin_user = models.User(
        username="admin", 
        email="admin@example.com", 
        password_hash=get_password_hash("password"), 
        full_name="Admin User", 
        role="ADMIN", 
        is_active=True
    )
    manager_user = models.User(
        username="manager", 
        email="manager@example.com", 
        password_hash=get_password_hash("password"), 
        full_name="Manager User", 
        role="MANAGER", 
        is_active=True
    )
    emp_user = models.User(
        username="employee", 
        email="employee@example.com", 
        password_hash=get_password_hash("password"), 
        full_name="Employee User", 
        role="EMPLOYEE", 
        is_active=True
    )
    db.add_all([admin_user, manager_user, emp_user])
    db.commit()
    
    db.refresh(manager_user)
    db.refresh(emp_user)
    
    # Seed employee profile
    emp_profile = models.Employee(
        user_id=emp_user.id,
        manager_id=manager_user.id,
        full_name="Employee User",
        email="employee@example.com",
        department="Engineering",
        designation="Developer",
        status="BENCH"
    )
    db.add(emp_profile)
    db.commit()
    
    yield db
    
    # Teardown
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    def _auth_headers(role="ADMIN"):
        username = "admin"
        if role == "MANAGER": username = "manager"
        elif role == "EMPLOYEE": username = "employee"
        # We don't need a real token for mocked dependencies if we override, 
        # but since we hit the endpoints directly, we should login to get a real JWT.
        return username
    return _auth_headers

@pytest.fixture(scope="function")
def client_admin(client):
    response = client.post("/api/auth/login", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture(scope="function")
def client_manager(client):
    response = client.post("/api/auth/login", data={"username": "manager", "password": "password"})
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture(scope="function")
def client_employee(client):
    response = client.post("/api/auth/login", data={"username": "employee", "password": "password"})
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
