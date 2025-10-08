from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json

from app.services.websocket_manager import ConnectionManager
from app.services.game_service import GameService
from models import GameRead

router = APIRouter(prefix="/game", tags=["game"])

manager = ConnectionManager()

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
    except ValueError as exc: 
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    game_read = GameRead.model_validate(game)
    return {"status": "success", "data": game_read.model_dump()}


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
        game = await game_service.join_game_by_code(payload.join_code, payload.name, manager)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    game_read = GameRead.model_validate(game)
    data = game_read.model_dump()
    data["websocket_url"] = f"/game/ws/{game.id}"

    return {"status": "success", "data": data}

@router.post("/continue/{game_id}")
async def continue_game(game_id: int):
    game_service = GameService()
    try:
        game = await game_service.continue_game(game_id, manager)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    game_read = GameRead.model_validate(game)
    return {"status": "success", "data": game_read.model_dump()}


@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_name: str = None):
    await manager.connect(websocket, game_id, player_name)
    
    if player_name:
        await manager.broadcast(f"{player_name} joined the game", game_id)
    
    try:
        while True:
            data = await websocket.receive_text()

            message_data = json.loads(data)
            message_type = message_data.get("type")
           
            if message_type == "chat_message":
                await manager.broadcast(
                    message_data, game_id
                )

    except WebSocketDisconnect:
        player_name = manager.get_player_name(websocket)
        manager.disconnect(websocket)
        if player_name != "Unknown Player":
            await manager.broadcast(f"{player_name} left the game", game_id)
