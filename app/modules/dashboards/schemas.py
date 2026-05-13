from pydantic import BaseModel
from typing import List, Dict, Any

class PieChartData(BaseModel):
    labels: List[str]
    values: List[int]

class BarChartData(BaseModel):
    labels: List[str]
    values: List[int]

class PaymentStatusSummary(BaseModel):
    pending: int = 0
    paid: int = 0
    rejected: int = 0
    cancelled: int = 0

class ClientDashboardOut(BaseModel):
    company_info: Dict[str, Any]
    total_orders: int
    orders_by_status: Dict[str, int]
    total_paid: float
    cart_products_count: int
    payment_status: PaymentStatusSummary
    incidents: List[Dict[str, Any]]
    orders_pie: PieChartData
    orders_bar: BarChartData
    recent_activity: List[str]
    total_products: int

class AdvisorDashboardOut(BaseModel):
    companies_info: List[Dict[str, Any]]  # Igual que el admin
    companies_pie: PieChartData
    total_clients: int
    total_orders: int
    orders_by_status: Dict[str, int]
    products_managed: int
    payment_status: PaymentStatusSummary
    incidents: List[Dict[str, Any]]
    orders_pie: PieChartData
    orders_bar: BarChartData
    recent_activity: List[str]

class AdminDashboardOut(BaseModel):
    total_users: int
    total_clients: int
    total_advisors: int
    total_admins: int
    total_companies: int
    active_companies: int
    inactive_companies: int
    total_orders: int
    total_payments: float
    total_products: int
    active_products: int
    inactive_products: int
    products_in_carts: int
    payment_status: PaymentStatusSummary
    orders_by_status: Dict[str, int]
    user_roles_pie: PieChartData
    orders_pie: PieChartData
    products_pie: PieChartData
    orders_bar: BarChartData
    payments_bar: BarChartData
    incidents: List[Dict[str, Any]]
    recent_activity: List[str]
