# app/modules/companies/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.deps import get_db
from app.core.auth import get_current_user
from app.modules.companies import services
from app.modules.companies.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)
from app.modules.users.models import User as UserModel

router = APIRouter(prefix="/companies", tags=["Companies"])


def get_role_name(user: UserModel) -> str:
    return (user.role.name or "").strip().lower() if user.role else ""


@router.get("/", response_model=List[CompanyResponse])
def get_companies(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    companies = services.get_companies(db)
    if not companies:
        raise HTTPException(status_code=404, detail="No hay empresas registradas")
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    company = services.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return company


@router.post("/", response_model=CompanyResponse)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    try:
        company = services.create_company(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not company:
        raise HTTPException(status_code=400, detail="El RFC ya está registrado")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    company = services.update_company(db, company_id, data)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return company


@router.patch("/{company_id}/active", response_model=CompanyResponse)
def toggle_active(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    company = services.toggle_company_active(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return company