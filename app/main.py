from fastapi import FastAPI
from app.core.config import settings
from app.db.base import Base
from sqlalchemy.orm import Session
from app.db.deps import get_db

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0"
)

@app.get("/")
def root():
    return {"status": "Lumisa Backend ejecutandose correctamente!"}