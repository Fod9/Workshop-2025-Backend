from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.game_service import GameService

router = APIRouter(prefix="/game", tags=["game"])

class GameCreatePayload(BaseModel):
    name: str
    host_name: str


class GameJoinPayload(BaseModel):
    join_code: str
    name: str


@router.post("/create")
async def create_game(payload: GameCreatePayload):
    game_service = GameService()
    try:
        game = game_service.create_game(payload.name, payload.host_name)
    except ValueError as exc:  # invalid player
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "data": game}


@router.post("/join")
async def join_game(payload: GameJoinPayload):
    game_service = GameService()
    try:
        game = game_service.join_game_by_code(payload.join_code, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "data": game}
