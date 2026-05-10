from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.modules.users.models import User
from app.utils.jwt import create_access_token




def authenticate_user(db: Session, email: str, password: str) -> tuple[Optional[User], Optional[str]]:
    """
    Autentica un usuario por email y contraseña.
    Retorna (usuario, None) si es válido y activo.
    Si falla, retorna (None, mensaje de error específico).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None, "Usuario no encontrado"
    if not verify_password(password, user.password_hash):
        return None, "Contraseña incorrecta"
    if not user.active:
        return None, "Usuario inactivo. Contacte al administrador."
    return user, None



def login(db: Session, email: str, password: str) -> tuple[Optional[tuple[str, User]], Optional[str]]:
    """
    Autentica y retorna (token JWT, usuario) si es válido.
    Si falla, retorna (None, mensaje de error específico).
    """
    user, error = authenticate_user(db, email, password)
    if not user:
        return None, error
    token = create_access_token({"sub": str(user.id)})
    return (token, user), None
