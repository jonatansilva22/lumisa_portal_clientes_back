import bcrypt

_MAX_BCRYPT_BYTES = 71

def _truncate_password_bytes(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= _MAX_BCRYPT_BYTES:
        return password_bytes
    return password_bytes[:_MAX_BCRYPT_BYTES]

def hash_password(password: str) -> str:
    password_bytes = _truncate_password_bytes(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    password_bytes = _truncate_password_bytes(password)
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)