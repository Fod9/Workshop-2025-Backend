from fastapi import FastAPI
from app.routes.room import router as room_router
from app.routes.user import router as user_router
from app.services.db_service import DBService

db_service = DBService()
db_service.create_database()

app = FastAPI()

app.include_router(room_router)
app.include_router(user_router)