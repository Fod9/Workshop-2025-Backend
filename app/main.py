from fastapi import FastAPI
from app.routes.room import router as room_router
from app.routes.user import router as user_router

app = FastAPI()

app.include_router(room_router)
app.include_router(user_router)