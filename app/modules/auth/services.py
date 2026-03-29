from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.modules.users.models import User
from app.utils.jwt import create_access_token



def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    # Retorna un objeto User si las credenciales son válidas, sino None.
    # Valida la contraseña usando hash seguro.

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login(db: Session, email: str, password: str) -> Optional[tuple[str, User]]:
    # Autentica y retorna token JWT + usuario.

    user = authenticate_user(db, email, password)
    if not user:
        return None

    token = create_access_token({"sub": str(user.id)})
    return token, user
