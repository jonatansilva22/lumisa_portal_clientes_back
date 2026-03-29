from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth import schemas, services
from app.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(credentials: schemas.Login, db: Session = Depends(get_db)):
    # Autentica el usuario y emite un token JWT con sus datos.

    result = services.login(db, credentials.email, credentials.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, user = result
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
