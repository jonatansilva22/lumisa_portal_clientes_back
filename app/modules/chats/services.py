# app/modules/chats/services.py
from sqlalchemy.orm import Session
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