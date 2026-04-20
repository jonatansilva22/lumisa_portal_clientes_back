from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class OrderDetailBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetailOut(OrderDetailBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    description: Optional[str] = None
    company_id: int

class OrderCreate(OrderBase):
    pass


class UserShortOut(BaseModel):
    id: int
    name: str
    last_name: str
    class Config:
        orm_mode = True

class CompanyShortOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class OrderOut(OrderBase):
    id: int
    folio: str
    total_payment: Decimal
    status_id: int
    client: UserShortOut
    advisor: Optional[UserShortOut]
    company: CompanyShortOut
    order_details: List[OrderDetailOut]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        orm_mode = True

class OrderStatusOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
