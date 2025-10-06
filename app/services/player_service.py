from services.db_service import DBService

class PlayerService:
    def __init__(self, db_service: DBService):
        self.db_service = db_service

    def create_player(self, username: str) -> None:
        create_statement = "INSERT INTO player (username) VALUES (:username)"
        result = self.db_service.execute(create_statement, {"username": username})
        print(result)
        return result
        