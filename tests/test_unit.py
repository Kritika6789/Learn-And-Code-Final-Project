import pytest
from fastapi import HTTPException
from server.auth import validate_password, verify_password, get_password_hash

def test_validate_password_valid():
    # Should pass without raising an exception
    validate_password("Password123")
    validate_password("StrongP@ssw0rd")

def test_validate_password_too_short():
    with pytest.raises(HTTPException) as excinfo:
        validate_password("Pass1")
    assert excinfo.value.status_code == 400
    assert "at least 8 characters" in excinfo.value.detail

def test_validate_password_no_uppercase():
    with pytest.raises(HTTPException) as excinfo:
        validate_password("password123")
    assert excinfo.value.status_code == 400
    assert "uppercase letter" in excinfo.value.detail

def test_validate_password_no_digit():
    with pytest.raises(HTTPException) as excinfo:
        validate_password("Password")
    assert excinfo.value.status_code == 400
    assert "numeric digit" in excinfo.value.detail

def test_password_hashing():
    password = "SuperSecretPassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False

def test_is_monday_logic():
    from datetime import date
    
    # 2026-06-01 is a Monday
    monday = date(2026, 6, 1)
    assert monday.weekday() == 0
    
    # 2026-06-02 is a Tuesday
    tuesday = date(2026, 6, 2)
    assert tuesday.weekday() != 0

def test_future_date_logic():
    from datetime import date, timedelta
    
    today = date.today()
    future_date = today + timedelta(days=7)
    past_date = today - timedelta(days=7)
    
    assert future_date > today
    assert past_date <= today
