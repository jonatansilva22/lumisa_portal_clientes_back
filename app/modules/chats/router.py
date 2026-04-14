# app/modules/chats/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.deps import get_db
from app.core.auth import get_current_user
from app.modules.chats import services
from app.modules.chats.schemas import ChatCreate, ChatResponse, ChatMarkRead
from app.modules.users.models import User as UserModel

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("/order/{order_id}", response_model=List[ChatResponse])
def get_messages(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    messages = services.get_messages_by_order(db, order_id)
    return messages


@router.post("/", response_model=ChatResponse)
def send_message(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
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