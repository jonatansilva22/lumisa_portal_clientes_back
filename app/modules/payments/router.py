from fastapi import Request, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import mercadopago
import os
from app.db.deps import get_db
from app.modules.payments import services, schemas
from app.utils.auth import get_current_user
from app.modules.users.models import User
from app.modules.payments.models import Payment
from app.modules.orders.models import Order
from app.modules.products.models import Product
from app.modules.payments.models import PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=schemas.PaymentWithMPOut, status_code=status.HTTP_201_CREATED)
def create_payment(payment_in: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        payment, mp_init_point = services.create_payment(db, payment_in)
        return {**schemas.PaymentOut.from_orm(payment).dict(), "mp_init_point": mp_init_point}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.get("/methods", response_model=List[schemas.PaymentMethodOut])
def get_payment_methods(db: Session = Depends(get_db)):
    return services.get_payment_methods(db)

@router.get("/statuses", response_model=List[schemas.PaymentStatusOut])
def get_payment_statuses(db: Session = Depends(get_db)):
    """Devuelve todos los estados posibles de pago."""
    return db.query(PaymentStatus).all()

@router.get("/order/{order_id}", response_model=List[schemas.PaymentOut])
def get_payments_by_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return services.get_payments_by_order(db, order_id)

# PATCH para actualizar el estado de pagos manuales (efectivo/transferencia)
@router.patch("/{payment_id}/update-status", status_code=status.HTTP_200_OK)
def update_manual_payment_status(payment_id: int, new_status_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Permite al asesor/admin cambiar el estado de un pago manual (efectivo/transferencia) pendiente a pagado, cancelado o rechazado.
    Si se marca como pagado, también cambia el estado del pedido a pagado y descuenta stock.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if payment.status_id != 1:
        raise HTTPException(status_code=400, detail="Solo se pueden modificar pagos en estado pendiente")
    if payment.method_id not in [2, 3]:
        raise HTTPException(status_code=400, detail="Solo se pueden modificar pagos de tipo transferencia o efectivo")
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if new_status_id == 2:  # Pagado
        # Validar stock antes de marcar como pagado
        productos_actualizados = []
        for detail in order.order_details:
            product = db.query(Product).filter(Product.id == detail.product_id).with_for_update().first()
            if not product or product.quantity < detail.quantity:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {detail.product_id}")
            product.quantity -= detail.quantity
            productos_actualizados.append(product)
        for product in productos_actualizados:
            db.add(product)
        payment.status_id = 2  # Pagado
        payment.paid_at = datetime.utcnow()
        db.add(payment)
        order.status_id = 5  # Pagado
        db.add(order)
        db.commit()
        return {"status": "pago validado y pedido actualizado"}
    elif new_status_id == 3:  # Rechazado
        payment.status_id = 3
        db.add(payment)
        db.commit()
        return {"status": "pago marcado como rechazado"}
    elif new_status_id == 4:  # Cancelado
        payment.status_id = 4
        db.add(payment)
        db.commit()
        return {"status": "pago marcado como cancelado"}
    else:
        raise HTTPException(status_code=400, detail="Estado no permitido")


# Webhook de MercadoPago
@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    print("[MP Webhook] Cuerpo recibido:", data)
    payment_id = data.get("data", {}).get("id") or data.get("id")
    if not payment_id:
        print("[MP Webhook] No se recibió payment_id")
        return {"status": "no payment id"}
    mp = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))
    payment_info = mp.payment().get(payment_id)
    mp_payment = payment_info.get("response", {})
    print(f"[MP Webhook] Detalle del pago (ID {payment_id}): status={mp_payment.get('status')}, status_detail={mp_payment.get('status_detail')}, external_reference={mp_payment.get('external_reference')}")
    order_id = mp_payment.get("external_reference")
    if not order_id:
        print("[MP Webhook] No se recibió external_reference (order_id)")
        return {"status": "no order id"}
    order = db.query(Order).filter(Order.id == int(order_id)).first()
    if not order:
        print(f"[MP Webhook] No se encontró el pedido con id {order_id}")
        return {"status": "order not found"}
    # Buscar el pago pendiente más reciente para este pedido y método tarjeta
    payment = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.method_id == 1,  # MercadoPago
        Payment.status_id == 1   # pendiente
    ).order_by(Payment.id.desc()).first()
    if mp_payment.get("status") == "approved":
        # Validar stock y descontar
        productos_actualizados = []
        for detail in order.order_details:
            product = db.query(Product).filter(Product.id == detail.product_id).with_for_update().first()
            if not product or product.quantity < detail.quantity:
                print(f"[MP Webhook] Stock insuficiente para producto {detail.product_id}")
                return {"status": f"stock insuficiente para producto {detail.product_id}"}
            product.quantity -= detail.quantity
            productos_actualizados.append(product)
        for product in productos_actualizados:
            db.add(product)
        if payment:
            payment.status_id = 2  # Pagado
            payment.paid_at = datetime.utcnow()
            db.add(payment)
        else:
            payment = Payment(
                amount=mp_payment.get("transaction_amount"),
                order_id=order.id,
                method_id=1,
                status_id=2,  # pagado
                paid_at=datetime.utcnow()
            )
            db.add(payment)
        order.status_id = 5  # Pagado
        db.add(order)
        db.commit()
        print(f"[MP Webhook] Pago registrado y pedido actualizado. order_id={order.id}, payment_id={payment_id}")
        return {"status": "ok"}
    else:
        # Si el pago fue rechazado o fallido, marcar como rechazado
        if payment:
            payment.status_id = 3  # Rechazado
            db.add(payment)
            db.commit()
            print(f"[MP Webhook] Pago marcado como rechazado. order_id={order.id}, payment_id={payment_id}")
            return {"status": "rejected", "mp_status": mp_payment.get("status"), "mp_status_detail": mp_payment.get("status_detail")}
        else:
            print(f"[MP Webhook] No se encontró pago pendiente para rechazar. order_id={order.id}, payment_id={payment_id}")
            return {"status": "no pending payment to reject", "mp_status": mp_payment.get("status"), "mp_status_detail": mp_payment.get("status_detail")}
