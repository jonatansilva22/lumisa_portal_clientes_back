from sqlalchemy.orm import Session
from app.modules.carts.models import Cart, CartDetail
from app.modules.carts.schemas import CartDetailCreate, CartDetailUpdate
from app.modules.products.models import Product
from app.modules.users.models import User
from typing import Optional
from sqlalchemy.exc import NoResultFound

def get_cart_by_user(db: Session, user_id: int) -> Optional[Cart]:
    return db.query(Cart).filter(Cart.user_id == user_id, Cart.active.is_(True)).first()

def create_cart(db: Session, user: User) -> Cart:
    cart = Cart(user_id=user.id, active=True)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def add_product_to_cart(db: Session, cart: Cart, payload: CartDetailCreate) -> CartDetail:
    product = db.query(Product).filter(Product.id == payload.product_id, Product.active.is_(True)).first()
    if not product:
        raise ValueError("Producto no encontrado o inactivo")
    cart_detail = db.query(CartDetail).filter(CartDetail.cart_id == cart.id, CartDetail.product_id == payload.product_id).first()
    nueva_cantidad = payload.quantity
    if cart_detail:
        total_cantidad = cart_detail.quantity + nueva_cantidad
        if total_cantidad > product.quantity:
            raise ValueError(f"No hay suficiente stock disponible. Stock actual: {product.quantity}")
        cart_detail.quantity = total_cantidad
    else:
        if nueva_cantidad > product.quantity:
            raise ValueError(f"No hay suficiente stock disponible. Stock actual: {product.quantity}")
        cart_detail = CartDetail(cart_id=cart.id, product_id=payload.product_id, quantity=nueva_cantidad, unit_price=product.price)
        db.add(cart_detail)
    db.commit()
    db.refresh(cart_detail)
    return cart_detail

def update_cart_detail(db: Session, cart_detail: CartDetail, payload: CartDetailUpdate) -> CartDetail:
    update_data = payload.dict(exclude_unset=True)
    if "quantity" in update_data:
        # Validar stock
        product = cart_detail.product
        nueva_cantidad = update_data["quantity"]
        if nueva_cantidad > product.quantity:
            raise ValueError(f"No hay suficiente stock disponible. Stock actual: {product.quantity}")
        cart_detail.quantity = nueva_cantidad
    db.add(cart_detail)
    db.commit()
    db.refresh(cart_detail)
    return cart_detail

def remove_product_from_cart(db: Session, cart: Cart, product_id: int) -> None:
    cart_detail = db.query(CartDetail).filter(CartDetail.cart_id == cart.id, CartDetail.product_id == product_id).first()
    if not cart_detail:
        raise ValueError("Producto no encontrado en el carrito")
    db.delete(cart_detail)
    db.commit()

def clear_cart(db: Session, cart: Cart) -> None:
    """
    Elimina todos los productos del carrito.
    """
    db.query(CartDetail).filter(CartDetail.cart_id == cart.id).delete()
    db.commit()
