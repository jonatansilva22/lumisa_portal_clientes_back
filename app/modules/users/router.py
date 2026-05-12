#Modulo Usuarios
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


def get_role_name(user: UserModel) -> str:
    return (user.role.name or "").strip().lower() if user.role else ""


@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = (
        (current_user.role.name or "").strip().lower()
        if current_user.role else ""
    )

    # Adinstrador pueder ambos roles
    if role_name == "administrador":
        users = services.get_users(db)

    # Asesor solo ve clientes
    elif role_name == "asesor":
        users = [
            u for u in services.get_users(db)
            if (u.role.name or "").strip().lower() == "cliente"
        ]

    # Otros roles no tienen permiso
    else:
        raise HTTPException(status_code=403, detail="No tiene permisos")

    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role_name = (
        (current_user.role.name or "").strip().lower()
        if current_user.role else ""
    )

    # Administrador puede ver cualquier usuario
    # Asesor puede ver clientes
    # Cliente solo puede ver su propio perfil
    if role_name == "administrador":
        pass 
    elif role_name == "asesor":
        target_user = services.get_user_by_id(db, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        target_role = (target_user.role.name or "").strip().lower()
        if target_role != "cliente" and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="No tiene permisos")
    else:
        # Cliente solo ve su perfil
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="No tiene permisos")

    user = services.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user


@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = (
        (current_user.role.name or "").strip().lower()
        if current_user.role else ""
    )

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
    role_name = (
        (current_user.role.name or "").strip().lower()
        if current_user.role else ""
    )

    # Solo admin puede editar usuarios, o el usuario puede editar su propio perfil
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
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="No puede cambiar la contraseña de otro usuario"
        )

    user = services.update_password(db, user_id, data)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Contrasena actual incorrecta"
        )

    return user


@router.patch("/{user_id}/active", response_model=UserResponse)
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role_name = (
        (current_user.role.name or "").strip().lower()
        if current_user.role else ""
    )

    # Solo administrador puede activar/desactivar usuarios
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")

    user = services.toggle_user_active(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    if role_name != "administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    try:
        result = services.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not result:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario eliminado correctamente"}