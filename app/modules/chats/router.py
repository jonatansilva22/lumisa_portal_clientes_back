# app/modules/chats/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.db.deps import get_db
from app.core.auth import get_current_user
from app.modules.chats import services
from app.modules.chats.schemas import ChatCreate, ChatResponse, ChatMarkRead, DirectMessageCreate
from app.modules.chats.models import Chat
from app.modules.users.models import User as UserModel
from app.modules.orders.models import Order

router = APIRouter(prefix="/chats", tags=["Chats"])


def get_role_name(user: UserModel) -> str:
    return (user.role.name or "").strip().lower() if user.role else ""


@router.get("/order/{order_id}", response_model=List[ChatResponse])
def get_messages(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    
    # Verificar que el pedido existe
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Validar permisos según rol
    if role_name == "administrador":
        # Admin puede ver todos los chats
        pass
    elif role_name == "asesor":
        # Asesor solo puede ver chats de pedidos asignados
        if order.advisor_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tiene permisos para ver este chat")
    elif role_name == "cliente":
        # Cliente solo puede ver chats de sus propios pedidos
        if order.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tiene permisos para ver este chat")
    else:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    messages = services.get_messages_by_order(db, order_id)
    return messages


@router.post("/", response_model=ChatResponse)
def send_message(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    role_name = get_role_name(current_user)
    
    # Admin no puede enviar mensajes (solo lectura)
    if role_name == "administrador":
        raise HTTPException(status_code=403, detail="El administrador no puede enviar mensajes")
    
    # Verificar que el pedido existe
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Validar permisos según rol
    if role_name == "asesor":
        # Asesor solo puede enviar en pedidos asignados
        if order.advisor_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tiene permisos para enviar mensajes en este pedido")
    elif role_name == "cliente":
        # Cliente solo puede enviar en sus propios pedidos
        if order.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tiene permisos para enviar mensajes en este pedido")
    else:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    return services.create_message(db, data, sender_id=current_user.id)


@router.patch("/read", response_model=ChatResponse)
def mark_message_read(
    data: ChatMarkRead,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    message = services.mark_as_read(db, data.message_id, current_user.id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return message


@router.get("/unread", response_model=List[ChatResponse])
def get_unread(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return services.get_unread_messages(db, current_user.id)


# ============= MENSAJES DIRECTOS =============

@router.get("/direct/conversations", response_model=List[dict])
def get_my_direct_conversations(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener lista de conversaciones directas del usuario actual"""
    
    # Obtener todos los mensajes directos donde el usuario es sender o receiver
    conversations = db.query(Chat).filter(
        Chat.order_id == None,
        or_(Chat.sender_id == current_user.id, Chat.receiver_id == current_user.id)
    ).all()
    
    # Extraer IDs únicos de usuarios con quien tiene conversación
    user_ids = set()
    for msg in conversations:
        if msg.sender_id != current_user.id:
            user_ids.add(msg.sender_id)
        if msg.receiver_id != current_user.id:
            user_ids.add(msg.receiver_id)
    
    # Obtener info de esos usuarios
    users = db.query(UserModel).filter(UserModel.id.in_(user_ids)).all()
    
    return [
        {
            "id": u.id,
            "name": u.name,
            "last_name": u.last_name,
            "email": u.email,
            "role_id": u.role_id,
            "role": {"id": u.role.id, "name": u.role.name} if u.role else None,
            "active": u.active
        }
        for u in users
    ]


@router.get("/direct/{user_id}", response_model=List[ChatResponse])
def get_direct_messages(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener mensajes directos entre el usuario actual y otro usuario"""
    
    # ✅ Ahora todos pueden ver mensajes directos
    messages = services.get_direct_messages(db, current_user.id, user_id)
    return messages


@router.post("/direct", response_model=ChatResponse)
def send_direct_message(
    data: DirectMessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Enviar un mensaje directo (sin order_id)"""
    
    # ✅ Ahora todos pueden enviar mensajes directos
    
    # Verificar que el receptor existe
    receiver = db.query(UserModel).filter(UserModel.id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Crear mensaje sin order_id
    new_message = services.create_direct_message(
        db=db,
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        message=data.message
    )
    
    return new_message