# app/modules/notifications/events.py
from sqlalchemy import event
from sqlalchemy.orm import object_session
from sqlalchemy.orm.attributes import get_history

from app.modules.orders.models import Order
from app.modules.products.models import Product
from app.modules.chats.models import Chat
from app.modules.notifications.models import Notification


def _add_notification(db, user_id: int, type: str, message: str, order_id: int = None):
    """Agrega notificación a la sesión sin hacer commit (se commitea con la transacción padre)."""
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        order_id=order_id,
    )
    db.add(notification)


#Orders

@event.listens_for(Order, "after_insert")
def on_order_create(mapper, connection, target):
    db = object_session(target)
    if db is None:
        return
    _add_notification(
        db,
        user_id=target.client_id,
        type="order_new",
        message=f"Tu pedido {target.folio} ha sido creado exitosamente.",
        order_id=target.id,
    )


@event.listens_for(Order, "after_update")
def on_order_update(mapper, connection, target):
    db = object_session(target)
    if db is None:
        return

    # Cambio de estado
    history_status = get_history(target, "status_id")
    if history_status.deleted:
        _add_notification(
            db,
            user_id=target.client_id,
            type="order_status",
            message=f"Tu pedido {target.folio} cambió de estado.",
            order_id=target.id,
        )

    # Asesor asignado
    history_advisor = get_history(target, "advisor_id")
    if history_advisor.added and any(v is not None for v in history_advisor.added):
        # Notificar al cliente
        _add_notification(
            db,
            user_id=target.client_id,
            type="order_advisor",
            message=f"Se asignó un asesor a tu pedido {target.folio}.",
            order_id=target.id,
        )
        # Notificar al asesor
        _add_notification(
            db,
            user_id=target.advisor_id,
            type="order_advisor",
            message=f"Se te asignó el pedido {target.folio}.",
            order_id=target.id,
        )


#products

@event.listens_for(Product, "after_update")
def on_product_update(mapper, connection, target):
    db = object_session(target)
    if db is None:
        return

    # Cambio de precio: notificar a usuarios con el producto en carrito o pedidos activos
    history_price = get_history(target, "price")
    if history_price.deleted:
        notified = set()
        
        # Usuarios con el producto en carrito
        from app.modules.carts.models import CartDetail
        cart_items = db.query(CartDetail).filter(CartDetail.product_id == target.id).all()
        for cd in cart_items:
            cart = cd.cart
            if cart and cart.user_id not in notified:
                _add_notification(
                    db,
                    user_id=cart.user_id,
                    type="product_price",
                    message=f"El precio de '{target.name}' en tu carrito ha cambiado.",
                )
                notified.add(cart.user_id)
        
        # Usuarios con pedidos activos que contienen el producto
        from app.modules.orders.models import OrderDetail, OrderStatus
        active_statuses = db.query(OrderStatus.id).filter(
            OrderStatus.name.in_(["pendiente", "revisado", "autorizado"])
        ).all()
        active_status_ids = [s.id for s in active_statuses]
        
        if active_status_ids:
            order_details = db.query(OrderDetail).join(Order).filter(
                OrderDetail.product_id == target.id,
                Order.status_id.in_(active_status_ids)
            ).all()
            
            for od in order_details:
                order = od.order
                if order and order.client_id not in notified:
                    _add_notification(
                        db,
                        user_id=order.client_id,
                        type="product_price",
                        message=f"El precio de '{target.name}' en tu pedido {order.folio} ha cambiado.",
                        order_id=order.id,
                    )
                    notified.add(order.client_id)

    # Sin stock: notificar a usuarios que lo tienen en carrito
    history_qty = get_history(target, "quantity")
    if history_qty.deleted and target.quantity == 0:
        from app.modules.carts.models import CartDetail
        affected = db.query(CartDetail).filter(CartDetail.product_id == target.id).all()
        notified = set()
        for cd in affected:
            cart = cd.cart
            if cart and cart.user_id not in notified:
                _add_notification(
                    db,
                    user_id=cart.user_id,
                    type="product_stock",
                    message=f"'{target.name}' en tu carrito se ha agotado.",
                )
                notified.add(cart.user_id)

    # Stock bajo: notificar a admin y asesores
    if history_qty.deleted and 0 < target.quantity <= 10:
        from app.modules.users.models import User
        admins_and_advisers = db.query(User).filter(
            User.role_id.in_([1, 2]),
            User.active == True
        ).all()
        for staff in admins_and_advisers:
            _add_notification(
                db,
                user_id=staff.id,
                type="product_stock",
                message=f"Stock bajo: '{target.name}' tiene solo {target.quantity} unidades.",
            )


#chat

@event.listens_for(Chat, "after_insert")
def on_chat_message(mapper, connection, target):
    db = object_session(target)
    if db is None:
        return
    _add_notification(
        db,
        user_id=target.receiver_id,
        type="chat",
        message="Tienes un nuevo mensaje.",
        order_id=target.order_id,
    )