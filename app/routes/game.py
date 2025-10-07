from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.websocket_manager import manager
from fastapi import WebSocket, WebSocketDisconnect
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


@router.post("/delete")
async def delete_game(payload: GameJoinPayload):
    game_service = GameService()
    try:
        game = game_service.delete_game(payload.join_code, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "data": game}


@router.post("/join")
async def join_game(payload: GameJoinPayload):
    game_service = GameService()
    try:
        game = game_service.join_game_by_code(payload.join_code, payload.name)

        await manager.connect(websocket, game.id)
        await manager.broadcast(f"{payload.name} joined the game", game.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "data": game}


@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int):
    await manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message text was: {data}", game_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the game", game_id)