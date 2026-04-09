from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class CartDetailBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class CartDetailCreate(CartDetailBase):
    pass

class CartDetailUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)

class CartDetailOut(CartDetailBase):
    id: int
    unit_price: Decimal
    class Config:
        orm_mode = True

class CartBase(BaseModel):
    pass

class CartCreate(CartBase):
    pass

class CartOut(CartBase):
    id: int
    user_id: int
    active: bool
    cart_details: list[CartDetailOut] = []
    total: float = 0

    class Config:
        orm_mode = True

    @property
    def total(self) -> float:
        return float(sum(cd.quantity * float(cd.unit_price) for cd in self.cart_details))
