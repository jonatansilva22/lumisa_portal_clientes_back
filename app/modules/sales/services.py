from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta
from app.modules.orders.models import Order
from app.modules.payments.models import Payment
from app.modules.sales.schemas import SaleHistoryOut, SalesHistoryResponse, PurchaseHistoryOut, PurchaseHistoryResponse

def get_purchase_history(db: Session, user_id: int, period: Optional[str], start_date: Optional[date], end_date: Optional[date]) -> PurchaseHistoryResponse:
    if period:
        start, end = get_period_dates(period)
    else:
        start, end = start_date, end_date
    query = db.query(Order).join(Payment).filter(
        Order.client_id == user_id,
        Payment.status.has(name="Pagado")
    )
    if start:
        query = query.filter(Payment.paid_at >= start)
    if end:
        query = query.filter(Payment.paid_at <= end)
    orders = query.all()
    purchases = []
    total_spent = 0.0
    for order in orders:
        paid_payment = next((p for p in order.payments if p.status and p.status.name.lower() == "pagado"), None)
        if not paid_payment:
            continue
        # Nuevos campos
        product_names = [detail.product.name for detail in order.order_details]
        products_price = float(sum(float(detail.unit_price) * detail.quantity for detail in order.order_details))
        shipping_price = float(order.shipping_price or 0)
        total_price = products_price + shipping_price
        total_spent += total_price
        purchases.append(PurchaseHistoryOut(
            order_id=order.id,
            folio=order.folio,
            company_id=order.company_id,
            company_name=order.company.name if order.company else "",
            total_payment=float(order.total_payment or 0),
            paid_at=paid_payment.paid_at.date() if paid_payment.paid_at else None,
            product_names=product_names,
            products_price=products_price,
            shipping_price=shipping_price,
            total_price=total_price
        ))
    return PurchaseHistoryResponse(
        total_purchases=len(purchases),
        total_spent=total_spent,
        purchases=purchases
    )

def get_period_dates(period: Optional[str]):
    today = date.today()
    if period == "monthly":
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == "yearly":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    else:
        start = None
        end = None
    return start, end

def get_sales_history(db: Session, period: Optional[str], start_date: Optional[date], end_date: Optional[date]) -> SalesHistoryResponse:
    if period:
        start, end = get_period_dates(period)
    else:
        start, end = start_date, end_date
    query = db.query(Order).join(Payment).filter(Payment.status.has(name="Pagado"))
    if start:
        query = query.filter(Payment.paid_at >= start)
    if end:
        query = query.filter(Payment.paid_at <= end)
    orders = query.all()
    sales = []
    total_earnings = 0.0
    for order in orders:
        paid_payment = next((p for p in order.payments if p.status and p.status.name.lower() == "pagado"), None)
        if not paid_payment:
            continue
        product_names = [detail.product.name for detail in order.order_details]
        products_price = float(sum(float(detail.unit_price) * detail.quantity for detail in order.order_details))
        shipping_price = float(order.shipping_price or 0)
        total_price = products_price + shipping_price
        total_earnings += total_price
        sales.append(SaleHistoryOut(
            order_id=order.id,
            folio=order.folio,
            client_id=order.client_id,
            client_name=order.client.name if order.client else "",
            company_id=order.company_id,
            company_name=order.company.name if order.company else "",
            total_payment=float(order.total_payment or 0),
            paid_at=paid_payment.paid_at.date() if paid_payment.paid_at else None,
            product_names=product_names,
            products_price=products_price,
            shipping_price=shipping_price,
            total_price=total_price
        ))
    return SalesHistoryResponse(
        total_sales=len(sales),
        total_earnings=total_earnings,
        sales=sales
    )
