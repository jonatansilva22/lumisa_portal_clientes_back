from sqlalchemy.orm import Session
from app.modules.carts.models import CartDetail

def is_product_in_any_cart(db: Session, product_id: int) -> bool:
    """
    Devuelve True si el producto está en algún carrito de compras.
    """
    return db.query(CartDetail).filter(CartDetail.product_id == product_id).first() is not None
