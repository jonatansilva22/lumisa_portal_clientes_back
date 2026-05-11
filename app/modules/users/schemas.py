from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

# schemas rol
class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# validador reutilizable
def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe tener al menos una mayúscula")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", password):
        raise ValueError("La contraseña debe tener al menos un carácter especial")
    return password

# para crear un usuario, lo que manda el admin
class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str
    role_id: int
    company_id: Optional[int] = None
    image_url: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        return validate_password_strength(v)

# Para actualizar perfil, lo que manda el usuario
class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    role_id: Optional[int] = None
    company_id: Optional[int] = None

# Para cambiar contraseña
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        return validate_password_strength(v)

# Lo que devuelve el sistema al consultar un usuario
class UserResponse(BaseModel):
    id: int
    name: str
    last_name: str
    email: str
    image_url: Optional[str] = None
    active: bool
    role: RoleResponse
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True