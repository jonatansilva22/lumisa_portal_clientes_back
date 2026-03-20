from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.modules.users import services
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    PasswordUpdate,
    UserResponse,
)
from app.modules.users.models import User as UserModel

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    role_name = (current_user.role.name or "").strip().lower() if current_user.role else ""
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    users = services.get_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No hay usuarios registrados")
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role_name = (current_user.role.name or "").strip().lower() if current_user.role else ""
    if role_name != "administrador" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    user = services.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    role_name = (current_user.role.name or "").strip().lower() if current_user.role else ""
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    try:
        user = services.create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not user:
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role_name = (current_user.role.name or "").strip().lower() if current_user.role else ""
    if role_name != "administrador" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    user = services.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}/password", response_model=UserResponse)
def update_password(
    user_id: int,
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role_name = (current_user.role.name or "").strip().lower() if current_user.role else ""
    if role_name != "administrador" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    user = services.update_password(db, user_id, data)
    if not user:
        raise HTTPException(status_code=400, detail="Contrasena actual incorrecta")
    return user


@router.patch("/{user_id}/active", response_model=UserResponse)
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role_name = (current_user.role.name or "").strip().lower() if current_user.role else ""
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    user = services.toggle_user_active(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user