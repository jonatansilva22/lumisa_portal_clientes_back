
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.utils.auth import get_current_user, admin_required, staff_required
from app.modules.dashboards import services, schemas
from app.modules.users.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/client", response_model=schemas.ClientDashboardOut)
def dashboard_cliente(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return services.get_dashboard_cliente(db, current_user)

@router.get("/advisor", response_model=schemas.AdvisorDashboardOut)
def dashboard_asesor(db: Session = Depends(get_db), current_user: User = Depends(staff_required)):
    return services.get_dashboard_asesor(db, current_user)

@router.get("/admin", response_model=schemas.AdminDashboardOut)
def dashboard_admin(db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    return services.get_dashboard_admin(db)
