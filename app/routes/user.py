from fastapi import APIRouter
from services.player_service import PlayerService
from services.db_service import DBService

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/create")
async def create_user(username: str):
    player_service = PlayerService()
    result = player_service.create_player(username)
    return {"status": "success", "data": result}

@router.get("/accept_request")
async def accept_request(player_id: int, request_id: int):
    pass