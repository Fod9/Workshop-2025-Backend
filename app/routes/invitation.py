from fastapi import APIRouter
from services.invitation_service import InvitationService

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
        return {"status": "success", "data": invitation}
    else:
        invitation = invitation_service.reject_invitation(invitation_id)
        return {"status": "success", "data": invitation}