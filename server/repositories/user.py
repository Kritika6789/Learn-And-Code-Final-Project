from sqlalchemy.orm import Session
from typing import Optional
from server.models import User
from server.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
