from fastapi import APIRouter
from services.invitation_service import InvitationService
from services.game_service import GameService

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.post("/send")
async def send_invitation(from_player_id: int, to_player_id: int, game_id: int):
    invitation_service = InvitationService()
    invitation = invitation_service.send_invitation(from_player_id, to_player_id, game_id)
    return {"status": "success", "data": invitation}


@router.post("/respond")
async def respond_invitation(invitation_id: int, accept: bool):
    invitation_service = InvitationService()
    if accept:
        invitation = invitation_service.accept_invitation(invitation_id)
        game_service = GameService()
        game_service.add_player_to_game(invitation.game_id, invitation.to_player_id)
        return {"status": "success", "data": {
            "invitation": invitation,
            "game_id": invitation.game_id,
            "player_id": invitation.to_player_id
        }}
    else:
        invitation = invitation_service.reject_invitation(invitation_id)
        return {"status": "success", "data": invitation}
    
