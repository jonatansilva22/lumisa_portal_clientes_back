from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field




class ProductTypeOut(BaseModel):
	id: int
	name: str

	model_config = ConfigDict(from_attributes=True)



class UnitOut(BaseModel):
	id: int
	name: str
	abbreviation: Optional[str] = None

	model_config = ConfigDict(from_attributes=True)



class ProductBase(BaseModel):
	name: str = Field(..., min_length=2, max_length=50)
	description: Optional[str] = None
	price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
	image_url: Optional[str] = Field(default=None, max_length=255)
	quantity: int = Field(..., ge=0)
	type_id: int = Field(..., gt=0)
	unit_id: int = Field(..., gt=0)
	active: bool = True



class ProductCreate(ProductBase):
	pass



class ProductUpdate(BaseModel):
	name: Optional[str] = Field(default=None, min_length=2, max_length=50)
	description: Optional[str] = None
	price: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
	image_url: Optional[str] = Field(default=None, max_length=255)
	quantity: Optional[int] = Field(default=None, ge=0)
	type_id: Optional[int] = Field(default=None, gt=0)
	unit_id: Optional[int] = Field(default=None, gt=0)
	active: Optional[bool] = None



class ProductOut(ProductBase):
	id: int
	created_at: datetime
	updated_at: Optional[datetime] = None
	type: Optional[ProductTypeOut] = None
	unit: Optional[UnitOut] = None

	model_config = ConfigDict(from_attributes=True)
