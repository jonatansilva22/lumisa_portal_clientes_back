from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth import schemas, services
from app.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(credentials: schemas.Login, db: Session = Depends(get_db)):
    """
    Autentica el usuario y emite un token JWT con sus datos.
    Retorna mensajes de error específicos para cada caso.
    """
    result, error = services.login(db, credentials.email, credentials.password)
    if error:
        # Mapear errores a diferentes códigos si se desea
        status_code = status.HTTP_401_UNAUTHORIZED
        if error == "Usuario inactivo. Contacte al administrador.":
            status_code = status.HTTP_403_FORBIDDEN
        elif error == "Usuario no encontrado":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status_code,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, user = result
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
