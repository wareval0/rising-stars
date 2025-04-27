from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.user_schema import UserCreate, UserLogin
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token, verify_password

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def signup(self, user_data: UserCreate):
        if self.repo.get_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if user_data.password1 != user_data.password2:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        self.repo.create(user_data)
        return {"message": "User created successfully"}

    def login(self, credentials: UserLogin):
        user = self.repo.get_by_email(credentials.username)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id)})
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }