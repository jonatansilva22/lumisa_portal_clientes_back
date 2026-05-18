import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, WebSocket, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.deps import get_db
from app.db.session import SessionLocal
from app.core.auth import get_current_user
from app.modules.chats import services
from app.modules.chats.schemas import ChatCreate, ChatResponse, ChatMarkRead, DirectMessageCreate
from app.modules.chats.models import Chat
from app.modules.chats.websocket_manager import chat_manager
from app.modules.users.models import User as UserModel
from app.modules.orders.models import Order
from app.utils.s3 import generate_presigned_url
from app.utils.jwt import decode_access_token

router = APIRouter(prefix="/chats", tags=["Chats"])

# Endpoint para obtener URL presignada de S3 para archivos de chat
@router.post("/s3-upload-url", response_model=dict)
def get_s3_upload_url(
    filename: str = Body(..., embed=True),
    content_type: str = Body(..., embed=True),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Devuelve una URL presignada para subir un archivo a S3 para el chat.
    """
    # Solo se usa para forzar autenticación en la generación de la URL.
    _ = current_user
    bucket = os.getenv("AWS_S3_BUCKET")
    if not bucket:
        raise HTTPException(status_code=500, detail="No está configurado el bucket de S3")
    key = f"chats/{filename}"
    url = generate_presigned_url(bucket, key, content_type)
    if not url:
        raise HTTPException(status_code=500, detail="No se pudo generar la URL presignada")
    return {"upload_url": url, "object_url": f"https://{bucket}.s3.amazonaws.com/{key}"}


def get_role_name(user: UserModel) -> str:
    return (user.role.name or "").strip().lower() if user.role else ""


def serialize_chat(message: Chat) -> dict:
    return jsonable_encoder(ChatResponse.model_validate(message))


def get_websocket_token(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token:
        return token

    auth_header = websocket.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1]

    return None


def get_current_user_from_token(db: Session, token: str | None) -> UserModel | None:
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if not user or not user.active:
        return None

    return user


def validate_order_chat_access(order: Order, user: UserModel, allow_send: bool = False) -> None:
    role_name = get_role_name(user)

    if role_name == "administrador":
        if allow_send:
            raise HTTPException(status_code=403, detail="El administrador no puede enviar mensajes")
        return

    if role_name == "asesor":
        if order.advisor_id != user.id:
            detail = "No tiene permisos para enviar mensajes en este pedido" if allow_send else "No tiene permisos para ver este chat"
            raise HTTPException(status_code=403, detail=detail)
        return

    if role_name == "cliente":
        if order.client_id != user.id:
            detail = "No tiene permisos para enviar mensajes en este pedido" if allow_send else "No tiene permisos para ver este chat"
            raise HTTPException(status_code=403, detail=detail)
        return

    raise HTTPException(status_code=403, detail="No tiene permisos")


async def close_websocket(websocket: WebSocket, code: int, detail: str) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "error", "detail": detail})
    await websocket.close(code=code)


@router.get("/order/{order_id}", response_model=List[ChatResponse])
def get_messages(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Verificar que el pedido existe
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_chat_access(order, current_user)
    
    messages = services.get_messages_by_order(db, order_id)
    return messages


@router.post("/", response_model=ChatResponse)
def send_message(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Permitir mensajes con texto, archivo o ambos
    if not data.message and not data.file_url:
        raise HTTPException(status_code=400, detail="Debes enviar un mensaje de texto o un archivo.")
    # Verificar que el pedido existe
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    validate_order_chat_access(order, current_user, allow_send=True)
    
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


@router.websocket("/ws/order/{order_id}")
async def websocket_order_chat(websocket: WebSocket, order_id: int):
    """Handle real-time order chat events."""
    db = SessionLocal()
    connected = False

    try:
        current_user = get_current_user_from_token(db, get_websocket_token(websocket))
        if not current_user:
            await close_websocket(websocket, status.WS_1008_POLICY_VIOLATION, "Token inválido o expirado")
            return

        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            await close_websocket(websocket, status.WS_1008_POLICY_VIOLATION, "Pedido no encontrado")
            return

        try:
            validate_order_chat_access(order, current_user)
        except HTTPException as exc:
            await close_websocket(websocket, status.WS_1008_POLICY_VIOLATION, exc.detail)
            return

        await chat_manager.connect_order(order_id, websocket)
        connected = True

        history = services.get_messages_by_order(db, order_id)
        await websocket.send_json({
            "type": "history",
            "messages": [serialize_chat(message) for message in history],
        })

        while True:
            payload = await websocket.receive_json()
            action = payload.get("action")

            if action == "send_message":
                try:
                    validate_order_chat_access(order, current_user, allow_send=True)
                except HTTPException as exc:
                    await websocket.send_json({"type": "error", "detail": exc.detail})
                    continue

                data = ChatCreate(
                    order_id=order_id,
                    receiver_id=payload.get("receiver_id"),
                    message=payload.get("message", ""),
                    file_url=payload.get("file_url"),
                )

                if not data.message and not data.file_url:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Debes enviar un mensaje de texto o un archivo.",
                    })
                    continue

                message = services.create_message(db, data, sender_id=current_user.id)
                serialized = serialize_chat(message)

                await chat_manager.broadcast_order(order_id, {
                    "type": "message_created",
                    "message": serialized,
                })
                await chat_manager.broadcast_users([message.sender_id, message.receiver_id], {
                    "type": "message_created",
                    "message": serialized,
                })

            elif action == "mark_read":
                message_id = payload.get("message_id")
                if not message_id:
                    await websocket.send_json({"type": "error", "detail": "message_id es obligatorio"})
                    continue

                message = services.mark_as_read(db, int(message_id), current_user.id)
                if not message:
                    await websocket.send_json({"type": "error", "detail": "Mensaje no encontrado"})
                    continue

                serialized = serialize_chat(message)
                await chat_manager.broadcast_order(order_id, {
                    "type": "message_read",
                    "message": serialized,
                })
                await chat_manager.broadcast_users([message.sender_id, message.receiver_id], {
                    "type": "message_read",
                    "message": serialized,
                })

            elif action == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "error", "detail": "Acción no soportada"})

    except WebSocketDisconnect:
        pass
    finally:
        if connected:
            chat_manager.disconnect_order(order_id, websocket)
        db.close()


@router.websocket("/ws/direct/{user_id}")
async def websocket_direct_chat(websocket: WebSocket, user_id: int):
    """Handle real-time direct chat events."""
    db = SessionLocal()
    connected = False
    current_user = None

    try:
        current_user = get_current_user_from_token(db, get_websocket_token(websocket))
        if not current_user:
            await close_websocket(websocket, status.WS_1008_POLICY_VIOLATION, "Token inválido o expirado")
            return

        receiver = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not receiver:
            await close_websocket(websocket, status.WS_1008_POLICY_VIOLATION, "Usuario no encontrado")
            return

        await chat_manager.connect_direct(current_user.id, user_id, websocket)
        connected = True

        history = services.get_direct_messages(db, current_user.id, user_id)
        await websocket.send_json({
            "type": "history",
            "messages": [serialize_chat(message) for message in history],
        })

        while True:
            payload = await websocket.receive_json()
            action = payload.get("action")

            if action == "send_message":
                message_text = payload.get("message", "")
                if not message_text:
                    await websocket.send_json({"type": "error", "detail": "El mensaje es obligatorio"})
                    continue

                new_message = services.create_direct_message(
                    db=db,
                    sender_id=current_user.id,
                    receiver_id=user_id,
                    message=message_text,
                )
                serialized = serialize_chat(new_message)

                await chat_manager.broadcast_direct(current_user.id, user_id, {
                    "type": "message_created",
                    "message": serialized,
                })
                await chat_manager.broadcast_users([new_message.sender_id, new_message.receiver_id], {
                    "type": "message_created",
                    "message": serialized,
                })

            elif action == "mark_read":
                message_id = payload.get("message_id")
                if not message_id:
                    await websocket.send_json({"type": "error", "detail": "message_id es obligatorio"})
                    continue

                message = services.mark_as_read(db, int(message_id), current_user.id)
                if not message:
                    await websocket.send_json({"type": "error", "detail": "Mensaje no encontrado"})
                    continue

                serialized = serialize_chat(message)
                await chat_manager.broadcast_direct(current_user.id, user_id, {
                    "type": "message_read",
                    "message": serialized,
                })
                await chat_manager.broadcast_users([message.sender_id, message.receiver_id], {
                    "type": "message_read",
                    "message": serialized,
                })

            elif action == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "error", "detail": "Acción no soportada"})

    except WebSocketDisconnect:
        pass
    finally:
        if connected and current_user:
            chat_manager.disconnect_direct(current_user.id, user_id, websocket)
        db.close()


@router.websocket("/ws")
async def websocket_chat_events(websocket: WebSocket):
    """Handle global real-time user chat events."""
    db = SessionLocal()
    current_user = None
    connected = False

    try:
        current_user = get_current_user_from_token(db, get_websocket_token(websocket))
        if not current_user:
            await close_websocket(websocket, status.WS_1008_POLICY_VIOLATION, "Token inválido o expirado")
            return

        await chat_manager.connect_user(current_user.id, websocket)
        connected = True

        unread = services.get_unread_messages(db, current_user.id)
        await websocket.send_json({
            "type": "unread_history",
            "messages": [serialize_chat(message) for message in unread],
        })

        while True:
            payload = await websocket.receive_json()
            action = payload.get("action")

            if action == "get_unread":
                unread = services.get_unread_messages(db, current_user.id)
                await websocket.send_json({
                    "type": "unread_history",
                    "messages": [serialize_chat(message) for message in unread],
                })
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "error", "detail": "Acción no soportada"})

    except WebSocketDisconnect:
        pass
    finally:
        if connected and current_user:
            chat_manager.disconnect_user(current_user.id, websocket)
        db.close()