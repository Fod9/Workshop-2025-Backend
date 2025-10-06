from fastapi import FastAPI
from app.routes.game import router as game_router
from app.services.db_service import DBService

db_service = DBService()
db_service.create_database()

app = FastAPI()

app.include_router(game_router)
