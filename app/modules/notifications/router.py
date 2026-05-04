from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.deps import get_db
from app.utils.auth import get_current_user
from app.modules.notifications import services
from app.modules.notifications.schemas import NotificationResponse, NotificationMarkRead
from app.modules.users.models import User as UserModel

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return services.get_notifications(db, current_user.id)


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    count = services.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.patch("/read")
def mark_as_read(
    data: NotificationMarkRead,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    notification = services.mark_as_read(db, data.notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notification


@router.patch("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    services.mark_all_as_read(db, current_user.id)
    return {"message": "Todas las notificaciones marcadas como leídas"}