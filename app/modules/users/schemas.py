from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# schemas rol
class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# schemas del usuario
# para crear un usuario, lo que manda el admin
class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str
    role_id: int
    company_id: Optional[int] = None
    image_url: Optional[str] = None

# Para actualizar perfil, lo que manda el usuario
class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None

# Para cambiar contraseña
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

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