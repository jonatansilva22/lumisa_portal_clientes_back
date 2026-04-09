from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.modules.carts import schemas, services
from app.utils.auth import get_current_user
from app.modules.users.models import User

router = APIRouter(prefix="/carts", tags=["carts"])

@router.get("/me", response_model=schemas.CartOut)
def get_my_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = services.get_cart_by_user(db, current_user.id)
    if not cart:
        cart = services.create_cart(db, current_user)
    total = sum(float(cd.quantity) * float(cd.unit_price) for cd in cart.cart_details)
    return schemas.CartOut(
        id=cart.id,
        user_id=cart.user_id,
        active=cart.active,
        cart_details=[
            schemas.CartDetailOut(
                id=cd.id,
                product_id=cd.product_id,
                quantity=cd.quantity,
                unit_price=cd.unit_price
            ) for cd in cart.cart_details
        ],
        total=total
    )

@router.post("/me", response_model=schemas.CartOut)
def add_product_to_my_cart(payload: schemas.CartDetailCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = services.get_cart_by_user(db, current_user.id)
    if not cart:
        cart = services.create_cart(db, current_user)
    try:
        services.add_product_to_cart(db, cart, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.refresh(cart)
    return schemas.CartOut(
        id=cart.id,
        user_id=cart.user_id,
        active=cart.active,
        cart_details=[
            schemas.CartDetailOut(
                id=cd.id,
                product_id=cd.product_id,
                quantity=cd.quantity,
                unit_price=cd.unit_price
            ) for cd in cart.cart_details
        ],
        total=sum(float(cd.quantity) * float(cd.unit_price) for cd in cart.cart_details)
    )

@router.put("/me/{product_id}", response_model=schemas.CartOut)
def update_product_in_my_cart(product_id: int, payload: schemas.CartDetailUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = services.get_cart_by_user(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")
    cart_detail = next((cd for cd in cart.cart_details if cd.product_id == product_id), None)
    if not cart_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado en el carrito")
    services.update_cart_detail(db, cart_detail, payload)
    db.refresh(cart)
    return schemas.CartOut(
        id=cart.id,
        user_id=cart.user_id,
        active=cart.active,
        cart_details=[
            schemas.CartDetailOut(
                id=cd.id,
                product_id=cd.product_id,
                quantity=cd.quantity,
                unit_price=cd.unit_price
            ) for cd in cart.cart_details
        ],
        total=sum(float(cd.quantity) * float(cd.unit_price) for cd in cart.cart_details)
    )

@router.delete("/me/{product_id}", response_model=schemas.CartOut)
def remove_product_from_my_cart(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = services.get_cart_by_user(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")
    try:
        services.remove_product_from_cart(db, cart, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.refresh(cart)
    return schemas.CartOut(
        id=cart.id,
        user_id=cart.user_id,
        active=cart.active,
        cart_details=[
            schemas.CartDetailOut(
                id=cd.id,
                product_id=cd.product_id,
                quantity=cd.quantity,
                unit_price=cd.unit_price
            ) for cd in cart.cart_details
        ],
        total=sum(float(cd.quantity) * float(cd.unit_price) for cd in cart.cart_details)
    )

@router.delete("/me/clear", response_model=schemas.CartOut)
def clear_my_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = services.get_cart_by_user(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")
    services.clear_cart(db, cart)
    db.refresh(cart)
    return schemas.CartOut(
        id=cart.id,
        user_id=cart.user_id,
        active=cart.active,
        cart_details=[
            schemas.CartDetailOut(
                id=cd.id,
                product_id=cd.product_id,
                quantity=cd.quantity,
                unit_price=cd.unit_price
            ) for cd in cart.cart_details
        ],
        total=sum(float(cd.quantity) * float(cd.unit_price) for cd in cart.cart_details)
    )
