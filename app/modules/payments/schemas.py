from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class PaymentBase(BaseModel):
    amount: Decimal
    order_id: int
    method_id: int

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    status_id: int
    paid_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True


# Esquema extendido para incluir el link de MercadoPago
class PaymentWithMPOut(PaymentOut):
    mp_init_point: Optional[str] = None
    class Config:
        from_attributes = True

class PaymentMethodOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class PaymentStatusOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
