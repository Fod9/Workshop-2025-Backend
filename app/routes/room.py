from fastapi import APIRouter

router = APIRouter()

@router.get("/rooms/{game_id}/{player_id}")
async def get_room(game_id: int, player_id: int):
    pass
