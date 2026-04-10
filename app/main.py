from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.db.base import Base
from sqlalchemy.orm import Session
from app.db.deps import get_db

# Importar modelos para que SQLAlchemy resuelva las relaciones
from app import models

#Aqui vamos a poner los import de nuestras funcionalidades (siempre los router)
from app.modules.auth import router as auth_router
from app.modules.products import router as products_router
from app.modules.users import router as users_router
from app.modules.companies import router as companies_router
from app.modules.carts import router as carts_router


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0"
)

setup_cors(app, settings.cors_origins)


#Y aqui vamos a incluir los routers de cada modulo, para que las rutas esten disponibles en la app
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(carts_router)

@app.get("/")
def root():
    return {"status": "Lumisa Backend ejecutandose correctamente!"}