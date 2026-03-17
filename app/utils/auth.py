from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.modules.users.models import User
from app.utils.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def _normalize_role(role_name: str | None) -> str:
    return (role_name or "").strip().lower()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    #Regresa el usuario autenticado a partir del token JWT.
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user


def require_roles(allowed_roles: Iterable[str]):
    #Crea una dependencia que valida el rol del usuario autenticado.
    allowed = {_normalize_role(role) for role in allowed_roles}

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        role_name = _normalize_role(current_user.role.name if current_user.role else None)
        if role_name not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta accion",
            )
        return current_user

    return role_dependency


admin_required = require_roles(["administrador", "admin"])
product_read_required = require_roles(["administrador", "admin", "asesor", "cliente"])