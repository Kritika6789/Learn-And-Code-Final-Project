from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from server import models, schemas, auth, scheduler
from server.database import engine, get_db
from server.dependencies import get_current_active_user
from server.routers import admin, manager, employee

app = FastAPI(title="PRM Tool API")
app.include_router(admin.router)
app.include_router(manager.router)
app.include_router(employee.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = ", ".join([f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"Validation Error: {msg}"},
    )

@app.on_event("startup")
def startup_event():
    scheduler.start_scheduler()

@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role, "force_password_change": user.force_password_change, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@app.post("/api/auth/change-password")
def change_password(new_password: str, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    auth.validate_password(new_password)
    current_user.password_hash = auth.get_password_hash(new_password)
    current_user.force_password_change = False
    db.commit()
    return {"message": "Password updated successfully"}

@app.get("/")
def root():
    return {"message": "PRM Tool API is running"}
