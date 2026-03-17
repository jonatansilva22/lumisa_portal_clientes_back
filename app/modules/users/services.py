from sqlalchemy.orm import Session
from app.modules.users.models import User, Role
from app.modules.users.schemas import UserCreate, UserUpdate, PasswordUpdate
from app.utils.password import hash_password, verify_password

# Obtener todos los usuarios
def get_users(db: Session):
    return db.query(User).all()

# Obtener un usuario por ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Crear un usuario nuevo (solo administrador)
def create_user(db: Session, data: UserCreate):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        return None

    new_user = User(
        name=data.name,
        last_name=data.last_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role_id=data.role_id,
        company_id=data.company_id,
        image_url=data.image_url,
        active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Actualizar perfil de usuario
def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    if data.name:
        user.name = data.name
    if data.last_name:          
        user.last_name = data.last_name  
    if data.image_url:
        user.image_url = data.image_url

    db.commit()      
    db.refresh(user)
    return user

# Cambio de contraseña
def update_password(db: Session, user_id: int, data: PasswordUpdate):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    if not verify_password(data.current_password, user.password_hash):
        return None

    user.password_hash = hash_password(data.new_password)
    db.commit()
    return user

# Activar o desactivar usuario
def toggle_user_active(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.active = not user.active
    db.commit()
    db.refresh(user)
    return user
