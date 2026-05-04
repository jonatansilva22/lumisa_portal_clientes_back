from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.cors import setup_cors
from app.db.base import Base
from sqlalchemy.orm import Session
from app.db.deps import get_db

from app import models

from app.modules.auth import router as auth_router
from app.modules.products import router as products_router
from app.modules.users import router as users_router
from app.modules.companies import router as companies_router
from app.modules.carts import router as carts_router
from app.modules.orders import router as orders_router
from app.modules.chats import router as chats_router
from app.modules.payments import router as payments_router
from app.modules.dashboards import router as dashboards_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#setup_cors(app, settings.cors_origins)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(carts_router)
app.include_router(orders_router)
app.include_router(chats_router)
app.include_router(payments_router)
app.include_router(dashboards_router)

@app.get("/")
def root():
    return {"status": "Lumisa Backend ejecutandose correctamente!"}