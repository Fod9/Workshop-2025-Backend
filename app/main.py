from fastapi import FastAPI
from app.routes.game import router as game_router
from app.services.db_service import DBService
from fastapi.middleware.cors import CORSMiddleware

# cors settings
origins = [
    "*",
]

db_service = DBService()
db_service.create_database()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router)
