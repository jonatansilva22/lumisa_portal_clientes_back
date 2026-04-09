from pydantic import BaseModel, EmailStr
from typing import Optional

class CompanyCreate(BaseModel):
    name: str
    rfc: str
    address: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    observations: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    observations: Optional[str] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    rfc: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    observations: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True