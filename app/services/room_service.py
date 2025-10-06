from services.db_service import DBService
from models import Game, Player

class GameService:
    def __init__(self, db_service: DBService | None = None) -> None:
        self.db_service = db_service or DBService()

    def create_room(self, game_id: int, player_id: int):
        with self.db_service.session() as session:
            game = Game(id=game_id, room_master_id=player_id)
            session.add(game)
            session.commit()
            return game 

    def delete_room(self, game_id: int):
        with self.db_service.session() as session:
            game = session.get(Game, game_id)
            if game:
                session.delete(game)
                session.commit()
                return True
            return False

    def register_player_to_room(self, game_id: int, player_id: int):
        with self.db_service.session() as session:
            game = session.get(Game, game_id)
            if game:
                player = session.get(Player, player_id)
                if player and player not in game.players:
                    game.players.append(player)
                    session.add(game)
                    session.commit()
                    return True
            return False