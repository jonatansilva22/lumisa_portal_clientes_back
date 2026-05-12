# app/modules/chats/services.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.modules.chats.models import Chat
from app.modules.chats.schemas import ChatCreate


# Obtener mensajes de un pedido
def get_messages_by_order(db: Session, order_id: int):
    return db.query(Chat).filter(Chat.order_id == order_id).order_by(Chat.sent_at).all()


# Enviar un mensaje
def create_message(db: Session, data: ChatCreate, sender_id: int):
    message = Chat(
        order_id=data.order_id,
        sender_id=sender_id,
        receiver_id=data.receiver_id,
        message=data.message,
        read=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


# Marcar mensaje como leido
def mark_as_read(db: Session, message_id: int, user_id: int):
    message = db.query(Chat).filter(
        Chat.id == message_id,
        Chat.receiver_id == user_id
    ).first()
    if not message:
        return None
    message.read = True
    db.commit()
    db.refresh(message)
    return message


# Obtener mensajes no leidos de un usuario
def get_unread_messages(db: Session, user_id: int):
    return db.query(Chat).filter(
        Chat.receiver_id == user_id,
        Chat.read == False
    ).all()


# MENSAJES DIRECTOS

# Obtener mensajes directos entre dos usuarios
def get_direct_messages(db: Session, user1_id: int, user2_id: int):
    """Obtener mensajes directos (order_id = NULL) entre dos usuarios"""
    return db.query(Chat).filter(
        Chat.order_id == None,
        or_(
            and_(Chat.sender_id == user1_id, Chat.receiver_id == user2_id),
            and_(Chat.sender_id == user2_id, Chat.receiver_id == user1_id)
        )
    ).order_by(Chat.sent_at).all()


# Crear mensaje directo (sin order_id)
def create_direct_message(db: Session, sender_id: int, receiver_id: int, message: str):
    """Crear un mensaje directo sin order_id"""
    new_message = Chat(
        order_id=None,  # Sin pedido asociado
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message,
        read=False,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

    