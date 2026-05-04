from sqlalchemy.orm import Session
from app.modules.notifications.models import Notification
from typing import List


def create_notification(db: Session, user_id: int, type: str, message: str, order_id: int = None) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        order_id=order_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications(db: Session, user_id: int) -> List[Notification]:
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()


def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).count()


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    if not notification:
        return None
    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int) -> None:
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).update({"read": True})
    db.commit()