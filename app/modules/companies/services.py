# app/modules/companies/services.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.companies.models import Company
from app.modules.companies.schemas import CompanyCreate, CompanyUpdate

# Obtener todas las empresas
def get_companies(db: Session):
    return db.query(Company).all()
# Obtener una empresa por ID
def get_company_by_id(db: Session, company_id: int):
    return db.query(Company).filter(Company.id == company_id).first()


# Crear una empresa nueva
def create_company(db: Session, data: CompanyCreate):
    existing = db.query(Company).filter(Company.rfc == data.rfc).first()
    if existing:
        return None

    new_company = Company(
        rfc=data.rfc,
        address=data.address,
        phone=data.phone,
        email=data.email,
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


# Actualizar una empresa
def update_company(db: Session, company_id: int, data: CompanyUpdate):
    company = get_company_by_id(db, company_id)
    if not company:
        return None

    if data.address:
        company.address = data.address
    if data.phone:
        company.phone = data.phone
    if data.email:
        company.email = data.email

    db.commit()
    db.refresh(company)
    return company


# Activar o desactivar empresa
def toggle_company_active(db: Session, company_id: int):
    company = get_company_by_id(db, company_id)
    if not company:
        return None

    company.active = not company.active
    db.commit()
    db.refresh(company)
    return company