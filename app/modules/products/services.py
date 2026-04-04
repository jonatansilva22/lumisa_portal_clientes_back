from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.products.models import Product, ProductType, Unit
from app.modules.products.schemas import ProductCreate, ProductUpdate
def get_product_types(db: Session) -> list[ProductType]:
    return db.query(ProductType).order_by(ProductType.name).all()


def get_units(db: Session) -> list[Unit]:
    return db.query(Unit).order_by(Unit.name).all()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> list[Product]:
    #Regresa una lista de productos con filtros opcionales.
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.active.is_(True))
    return query.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    #Regresa un producto por su id o ninguno si no existe.
    return db.query(Product).filter(Product.id == product_id).first()


def product_name_exists(db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
    #Validate unique product name ignoring case.
    query = db.query(Product).filter(func.lower(Product.name) == name.strip().lower())
    if exclude_id is not None:
        query = query.filter(Product.id != exclude_id)
    return db.query(query.exists()).scalar()


def _validate_fk_entities(db: Session, type_id: int, unit_id: int) -> None:
    #Lanza ValueError cuando las foreigk key son inválidas.
    type_exists = db.query(ProductType.id).filter(ProductType.id == type_id).first()
    if not type_exists:
        raise ValueError("El tipo de producto no existe")

    unit_exists = db.query(Unit.id).filter(Unit.id == unit_id).first()
    if not unit_exists:
        raise ValueError("La unidad no existe")


def create_product(db: Session, payload: ProductCreate) -> Product:
    #Crea un producto con las validaciones de negocio.
    if product_name_exists(db, payload.name):
        raise ValueError("Ya existe un producto con ese nombre")

    _validate_fk_entities(db, payload.type_id, payload.unit_id)

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    #Actualiza un producto existenten con payload parcial.
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return product

    if "name" in update_data and product_name_exists(db, update_data["name"], exclude_id=product.id):
        raise ValueError("Ya existe un producto con ese nombre")

    next_type_id = update_data.get("type_id", product.type_id)
    next_unit_id = update_data.get("unit_id", product.unit_id)
    _validate_fk_entities(db, next_type_id, next_unit_id)

    for key, value in update_data.items():
        setattr(product, key, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    #Elimina un producto permanentemente.
    db.delete(product)
    db.commit()
