from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.modules.products import schemas, services
from app.modules.users.models import User
from app.utils.auth import admin_required, product_read_required
from app.utils.s3 import generate_presigned_url
import os
from app.utils.products import is_product_in_any_cart

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/s3-upload-url", response_model=dict)
def get_s3_upload_url(
    module: str = Body(..., embed=True),
    filename: str = Body(..., embed=True),
    content_type: str = Body(..., embed=True),
    _current_user: User = Depends(admin_required),
):
    """
    Devuelve una URL presignada para subir un archivo a S3 para cualquier módulo. Solo admin.
    """
    bucket = os.getenv("AWS_S3_BUCKET")
    if not bucket:
        raise HTTPException(status_code=500, detail="No está configurado el bucket de S3")
    key = f"{module}/{filename}"
    url = generate_presigned_url(bucket, key, content_type)
    if not url:
        raise HTTPException(status_code=500, detail="No se pudo generar la URL presignada")
    return {"upload_url": url, "object_url": f"https://{bucket}.s3.amazonaws.com/{key}"}

@router.get("/types", response_model=list[schemas.ProductTypeOut])
def list_product_types(
    db: Session = Depends(get_db),
    _current_user: User = Depends(product_read_required),
):
    #Lista todos los tipos de producto para cualquier usuario con permiso de lectura.
    return services.get_product_types(db)


@router.get("/units", response_model=list[schemas.UnitOut])
def list_units(
    db: Session = Depends(get_db),
    _current_user: User = Depends(product_read_required),
):
    #Lista todas las unidades para cualquier usuario con permiso de lectura.
    return services.get_units(db)

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
    current_user: User = Depends(product_read_required),
):
    # Solo clientes y asesores: no pueden ver productos inactivos
    role_name = (current_user.role.name or "").lower()
    if role_name in ["cliente", "asesor"]:
        product = services.get_product_by_id(db, product_id, active_only=True)
    else:
        product = services.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado o inactivo")
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
    product = services.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if is_product_in_any_cart(db, product_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar: el producto está en uno o más carritos de compras.")
    services.delete_product(db, product)
    return None
