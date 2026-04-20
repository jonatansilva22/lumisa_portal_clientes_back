from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.orders.models import Order, OrderDetail, OrderStatus
from app.modules.orders.schemas import OrderCreate
from app.modules.carts.models import Cart, CartDetail
from app.modules.users.models import User
from app.modules.products.models import Product
from sqlalchemy import select
from typing import List, Optional

def create_order_from_cart(db: Session, user: User) -> Order:
    cart = db.query(Cart).filter(Cart.user_id == user.id, Cart.active == True).first()
    if not cart or not cart.cart_details:
        raise ValueError("El carrito está vacío.")
    # Crear la orden
    order = Order(
        folio="",  # Se debe generar un folio único
        description=None,
        total_payment=sum(cd.quantity * cd.unit_price for cd in cart.cart_details),
        status_id=1,  # Estado inicial: pendiente
        client_id=user.id,
        advisor_id=None,  # El asesor se asigna después
        company_id=user.company_id if hasattr(user, 'company_id') else 1,  # Adaptado a nuestro modelo
    )
    db.add(order)
    db.flush()  # Para obtener el id de la orden
    # Generar folio con letra y número correlativo
    max_per_letter = 1000000  # 000000 a 999999
    letter_index = (order.id - 1) // max_per_letter
    number_part = (order.id - 1) % max_per_letter
    if letter_index >= 26:
        # Si se supera la Z, usar AA, AB, etc. (opcional, aquí solo A-Z)
        raise ValueError("Se ha superado el límite de folios (Z999999)")
    letter = chr(ord('A') + letter_index)
    order.folio = f"{letter}{number_part:06d}"
    # Agregar detalles
    for cd in cart.cart_details:
        order_detail = OrderDetail(
            order_id=order.id,
            product_id=cd.product_id,
            quantity=cd.quantity,
            unit_price=cd.unit_price,
        )
        db.add(order_detail)
    # Vaciar el carrito
    db.query(CartDetail).filter(CartDetail.cart_id == cart.id).delete()
    db.commit()
    db.refresh(order)
    return order

def get_orders_by_user(db: Session, user_id: int) -> List[Order]:
    return db.query(Order).filter(Order.client_id == user_id).all()

def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()

def cancel_order(db: Session, order: Order, user: User):
    if order.client_id != user.id:
        raise ValueError("No autorizado para cancelar este pedido.")
    if order.status_id != 1:
        raise ValueError("Solo se pueden cancelar pedidos pendientes.")
    order.status_id = 4  # 4 = Cancelado
    db.commit()
    db.refresh(order)
    return order

def get_all_orders(db: Session) -> List[Order]:
    return db.query(Order).all()

# Asignar asesor a un pedido
def assign_advisor_to_order(db: Session, order: Order, advisor_id: int):
    order.advisor_id = advisor_id
    db.commit()
    db.refresh(order)
    return order

def update_order_status(db: Session, order: Order, new_status_id: int):
    # Obtener el nombre del nuevo estado
    new_status = db.query(OrderStatus).filter(OrderStatus.id == new_status_id).first()
    order.status_id = new_status_id
    db.commit()
    db.refresh(order)

    # Si el nuevo estado es 'pagado', descontar stock
    if new_status and new_status.name.lower() == 'pagado':
        for detail in order.order_details:
            product = db.query(Product).filter(Product.id == detail.product_id).first()
            if product:
                if product.quantity < detail.quantity:
                    raise ValueError(f"Stock insuficiente para el producto {product.name}")
                product.quantity -= detail.quantity
        db.commit()
        db.refresh(order)
    return order

def get_order_statuses(db: Session) -> List[OrderStatus]:
    return db.query(OrderStatus).all()
