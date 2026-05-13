from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
from app.db.deps import get_db
from app.modules.users.models import User
from app.modules.orders.models import Order
from app.modules.payments.models import Payment
from app.modules.companies.models import Company
from app.modules.sales.schemas import SaleHistoryFilter, SalesHistoryResponse, SaleHistoryOut, PurchaseHistoryResponse
from app.modules.sales import services
from app.utils.auth import get_current_user, admin_required, staff_required

router = APIRouter(prefix="/sales/history", tags=["sales-history"])


@router.get("/", response_model=SalesHistoryResponse)
def get_sales_history(
    period: Optional[str] = Query(None, enum=["monthly", "weekly", "yearly"]),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_required)
):
    # Solo admin y asesor pueden acceder
    return services.get_sales_history(db, period, start_date, end_date)


# Historial de compras del cliente autenticado
@router.get("/purchases", response_model=PurchaseHistoryResponse)
def get_purchase_history(
    period: Optional[str] = Query(None, enum=["monthly", "weekly", "yearly"]),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Permitir string vacío y convertir a None
    start = start_date if start_date and start_date.strip() else None
    end = end_date if end_date and end_date.strip() else None
    # Convertir a date si es necesario
    from datetime import date
    def parse_date(val):
        try:
            return date.fromisoformat(val)
        except Exception:
            return None
    start = parse_date(start) if start else None
    end = parse_date(end) if end else None
    return services.get_purchase_history(db, current_user.id, period, start, end)
