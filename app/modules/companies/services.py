from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.companies.models import Company
from app.modules.companies.schemas import CompanyCreate, CompanyUpdate

def get_companies(db: Session):
    return db.query(Company).all()

def get_company_by_id(db: Session, company_id: int):
    return db.query(Company).filter(Company.id == company_id).first()

def create_company(db: Session, data: CompanyCreate):
    # Validar RFC duplicado
    existing_rfc = db.query(Company).filter(Company.rfc == data.rfc).first()
    if existing_rfc:
        raise ValueError("El RFC ya está registrado")
    
    # Validar nombre duplicado
    existing_name = db.query(Company).filter(Company.name == data.name).first()
    if existing_name:
        raise ValueError("El nombre de empresa ya está registrado")

    new_company = Company(
        name=data.name,
        rfc=data.rfc,
        address=data.address,
        phone=data.phone,
        email=data.email,
        observations=data.observations,
        active=True
    )
    db.add(new_company)
    try:
        db.commit()
        db.refresh(new_company)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error de integridad: {str(e.orig)}")
    return new_company

def update_company(db: Session, company_id: int, data: CompanyUpdate):
    company = get_company_by_id(db, company_id)
    if not company:
        return None

    if data.name is not None:
        company.name = data.name
    if data.address is not None:
        company.address = data.address
    if data.phone is not None:
        company.phone = data.phone
    if data.email is not None:
        company.email = data.email
    if data.observations is not None:
        company.observations = data.observations

    db.commit()
    db.refresh(company)
    return company

def toggle_company_active(db: Session, company_id: int):
    company = get_company_by_id(db, company_id)
    if not company:
        return None

    company.active = not company.active
    db.commit()
    db.refresh(company)
    return company

def delete_company(db: Session, company_id: int):
    company = get_company_by_id(db, company_id)
    if not company:
        return None
    
    # Verificar si tiene usuarios asociados
    from app.modules.users.models import User
    has_users = db.query(User).filter(User.company_id == company_id).first()
    if has_users:
        raise ValueError("No se puede eliminar la empresa porque tiene clientes asociados. Desactívela en su lugar.")
    
    # Verificar si tiene pedidos asociados
    from app.modules.orders.models import Order
    has_orders = db.query(Order).filter(Order.company_id == company_id).first()
    if has_orders:
        raise ValueError("No se puede eliminar la empresa porque tiene pedidos asociados. Desactívela en su lugar.")
    
    db.delete(company)
    db.commit()
    return company