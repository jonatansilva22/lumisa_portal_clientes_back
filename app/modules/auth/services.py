from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.modules.users.models import User
from app.utils.jwt import create_access_token


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    #Retorna un objeto **User** si las credenciales son válidas, sino retorna ``None``.

    #La función busca en la base de datos un usuario con el email dado
    #y verifica la contraseña contra el hash almacenado usando
    #:func:`app.core.security.verify_password`.
    

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login(db: Session, email: str, password: str) -> Optional[str]:
    #Autentica y retorna un token JWT de acceso si tiene éxito.

    #Si la autenticación falla, la función retorna ``None`` para que la persona que llama
    #pueda lanzar un error HTTP apropiado. El payload del token actualmente contiene
    #solo el id del usuario bajo la claim ``sub``; otros claims se pueden agregar después.
    

    user = authenticate_user(db, email, password)
    if not user:
        return None

    token = create_access_token({"sub": str(user.id)})
    return token
