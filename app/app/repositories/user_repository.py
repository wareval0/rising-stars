from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_data: UserCreate):
        hashed_pw = get_password_hash(user_data.password1)
        user = User(
            nombre=user_data.nombre,
            apellido=user_data.apellido,
            ciudad=user_data.ciudad,
            pais=user_data.pais,
            email=user_data.email,
            hashed_password=hashed_pw
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user