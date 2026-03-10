from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    #Retorna un JWT codificado conteniendo ``data``.

    #data`` es copiado y la claim ``exp`` es agregada basado en el
    #expires_delta`` provisto o en ``settings.JWT_EXPIRE_MINUTES``.


    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    #Decodifica ``token`` y retorna su payload, o ``None`` si es inválido.

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
