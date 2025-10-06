from app.services.db_service import DBService
from models import Invitation, Player, Game

class InvitationService:
    def __init__(self, db_service: DBService | None = None) -> None:
        self.db_service = db_service or DBService()

    def send_invitation(self, from_player_id: int, to_player_id: int, game_id: int):
        with self.db_service.session() as session:
            invitation = Invitation(from_player_id=from_player_id, to_player_id=to_player_id, game_id=game_id)
            session.add(invitation)
            session.commit()
            return invitation

    def accept_invitation(self, invitation_id: int):
        with self.db_service.session() as session:
            invitation = session.get(Invitation, invitation_id)
            if not invitation:
                raise ValueError("Invitation not found")
            invitation.status = "accepted"
            session.add(invitation)
            session.commit()
            return invitation
    
    def reject_invitation(self, invitation_id: int):
        with self.db_service.session() as session:
            invitation = session.get(Invitation, invitation_id)
            if not invitation:
                raise ValueError("Invitation not found")
            invitation.status = "rejected"
            session.add(invitation)
            session.commit()
            return invitation

    def get_invitations_for_player(self, player_id: int):
        with self.db_service.session() as session:
            invitations = session.query(Invitation).filter(Invitation.to_player_id == player_id).all()
            return invitations