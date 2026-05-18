from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.deps import get_db
from app.modules.orders import services, schemas
from app.utils.auth import get_current_user, staff_required
from app.modules.users.models import User

router = APIRouter(prefix="/orders", tags=["orders"])

# Endpoint para crear pedido desde carrito
@router.post("/from-cart", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order_from_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return services.create_order_from_cart(db, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

# Endpoint para actualizar el precio de envío (solo staff)
@router.put("/{order_id}/shipping-price", response_model=schemas.OrderOut, dependencies=[Depends(staff_required)])
def update_shipping_price(order_id: int, shipping_price: float, db: Session = Depends(get_db)):
    order = services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return update_shipping_price_service(db, order, shipping_price)

# Importar la función correctamente del módulo services
from app.modules.orders.services import update_shipping_price as update_shipping_price_service

@router.get("/me", response_model=List[schemas.OrderOut])
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return services.get_orders_by_user(db, current_user.id)

@router.get("/me/{order_id}", response_model=schemas.OrderOut)
def get_my_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = services.get_order_by_id(db, order_id)
    if not order or order.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return order

@router.post("/me/{order_id}/cancel", response_model=schemas.OrderOut)
def cancel_my_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    try:
        return services.cancel_order(db, order, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.get("/", response_model=List[schemas.OrderOut], dependencies=[Depends(staff_required)])
def get_all_orders(db: Session = Depends(get_db)):
    return services.get_all_orders(db)

# Asignar asesor a un pedido
@router.get("/statuses", response_model=List[schemas.OrderStatusOut])
def get_order_statuses(db: Session = Depends(get_db)):
    return services.get_order_statuses(db)

@router.put("/{order_id}/assign-advisor", response_model=schemas.OrderOut, dependencies=[Depends(staff_required)])
def assign_advisor(order_id: int, advisor_id: int, db: Session = Depends(get_db)):
    order = services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return services.assign_advisor_to_order(db, order, advisor_id)

@router.put("/{order_id}/status", response_model=schemas.OrderOut, dependencies=[Depends(staff_required)])
def update_order_status(order_id: int, new_status_id: int, db: Session = Depends(get_db)):
    order = services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return services.update_order_status(db, order, new_status_id)
    
# Endpoint para que staff (admin/asesor) obtenga el detalle de un pedido por id
@router.get("/{order_id}", response_model=schemas.OrderOut, dependencies=[Depends(staff_required)])
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return order