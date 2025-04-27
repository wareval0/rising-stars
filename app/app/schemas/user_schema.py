from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    nombre: str
    apellido: str
    ciudad: str
    pais: str
    email: EmailStr
    password1: str
    password2: str

class UserLogin(BaseModel):
    username: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int