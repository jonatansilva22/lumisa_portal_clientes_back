# app/modules/companies/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional


# Para crear una empresa
class CompanyCreate(BaseModel):
    rfc: str
    address: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


# Para actualizar una empresa
class CompanyUpdate(BaseModel):
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


# Lo que devuelve el sistema al consultar una empresa
class CompanyResponse(BaseModel):
    id: int
    rfc: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True