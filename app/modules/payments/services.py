from sqlalchemy.orm import Session
from app.modules.payments.models import Payment, PaymentMethod, PaymentStatus
from app.modules.orders.models import Order
from app.modules.payments.schemas import PaymentCreate
from decimal import Decimal
from datetime import datetime
import mercadopago
import os

# Inicializa el SDK de MercadoPago con el Access Token
mp = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))

def create_payment(db: Session, payment_in: PaymentCreate) -> Payment:
    order = db.query(Order).filter(Order.id == payment_in.order_id).first()
    if not order:
        raise ValueError("Pedido no encontrado")
    # Solo permitir pagos para pedidos autorizados (status_id = 3)
    if order.status_id != 3:
        raise ValueError("Solo se pueden pagar pedidos con estado 'Autorizado'.")

    # Validar que todos los productos del pedido estén activos
    for detail in order.order_details:
        if not detail.product.active:
            raise ValueError(f"El producto {detail.product_id} está inactivo y no se puede pagar el pedido.")

    # Validar que no exista ya un pago pendiente para este pedido,
    # excepto si es de tarjeta (method_id == 1)
    if payment_in.method_id != 1:
        existing_payment = db.query(Payment).filter(
            Payment.order_id == payment_in.order_id,
            Payment.status_id == 1,  # pendiente
            Payment.method_id != 1    # no tarjeta
        ).first()
        if existing_payment:
            raise ValueError("Ya existe un pago pendiente para este pedido. Cancela o paga el anterior antes de crear uno nuevo.")

    # Si es MercadoPago (method_id == 1)
    if payment_in.method_id == 1:
        preference_data = {
            "items": [
                {
                    "title": f"Pago pedido #{order.folio}",
                    "quantity": 1,
                    "currency_id": "MXN",
                    "unit_price": float(payment_in.amount)
                }
            ],
            "external_reference": str(order.id)
        }
        preference = mp.preference().create(preference_data)
        mp_init_point = preference["response"].get("init_point")
    else:
        mp_init_point = None  # No link para efectivo/transferencia

    payment = Payment(
        amount=payment_in.amount,
        order_id=payment_in.order_id,
        method_id=payment_in.method_id,
        status_id=1,  # pendiente
        paid_at=None
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment, mp_init_point

def get_payment_methods(db: Session):
    return db.query(PaymentMethod).filter(PaymentMethod.active == True).all()

def get_payments_by_order(db: Session, order_id: int):
    return db.query(Payment).filter(Payment.order_id == order_id).all()
