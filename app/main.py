from fastapi import FastAPI
from app.routes.game import router as game_router
from app.services.db_service import DBService
from fastapi.middleware.cors import CORSMiddleware



#cors settings
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
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


#route to delete database - for testing purposes only
@app.delete("/reset-database")
async def reset_database():
    db_service.drop_database()
    db_service.create_database()
    return {"status": "success", "message": "Database reset successfully"}
