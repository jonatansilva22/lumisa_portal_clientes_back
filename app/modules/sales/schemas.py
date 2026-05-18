from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class SaleHistoryFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    period: Optional[str] = None  # 'monthly', 'weekly', 'yearly', or None

class SaleHistoryOut(BaseModel):
    order_id: int
    folio: str
    client_id: int
    client_name: str
    company_id: int
    company_name: str
    total_payment: float
    paid_at: date
    # Nuevos campos
    product_names: List[str]
    products_price: float
    shipping_price: float
    total_price: float
class SalesHistoryResponse(BaseModel):
    total_sales: int
    total_earnings: float
    sales: List[SaleHistoryOut]

# Modelos para historial de compras de cliente
class PurchaseHistoryOut(BaseModel):
    order_id: int
    folio: str
    company_id: int
    company_name: str
    total_payment: float
    paid_at: date
    # Nuevos campos
    product_names: List[str]
    products_price: float
    shipping_price: float
    total_price: float
class PurchaseHistoryResponse(BaseModel):
    total_purchases: int
    total_spent: float
    purchases: List[PurchaseHistoryOut]
