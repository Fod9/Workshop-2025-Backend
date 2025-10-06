from fastapi import APIRouter, Request
from services.game_service import GameService

router = APIRouter(prefix="/game", tags=["game"])

@router.post("/create")
def create_game(request: Request):
    game_service = GameService()
    game = game_service.create_game(request.player_id)
    return game


