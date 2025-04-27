from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.dependencies import get_db
from app.services.user_service import UserService
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup", status_code=201)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.signup(user_data)

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.login(credentials)

@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.nombre}!"}