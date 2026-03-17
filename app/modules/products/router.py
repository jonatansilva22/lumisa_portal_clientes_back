from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.modules.products import schemas, services
from app.modules.users.models import User
from app.utils.auth import admin_required, product_read_required

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[schemas.ProductOut])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    _current_user: User = Depends(product_read_required),
):
    #Lista de productos para el administrador, asesor y cliente.
    return services.get_products(db=db, skip=skip, limit=limit, active_only=active_only)


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(product_read_required),
):
    #Obtiene un producto por su id para el administrador, cliente y asesor.
    product = services.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product


@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_required),
):
    #Crea un producto, solo para el administrador.
    try:
        return services.create_product(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_required),
):
    #Actualiza un producto mediante su id. Solo para el administrador.
    product = services.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    try:
        return services.update_product(db, product, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_required),
):
    #Borra un producto mediante su id. Solo para el administrador.
    product = services.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    services.delete_product(db, product)
    return None
