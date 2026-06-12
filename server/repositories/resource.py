from sqlalchemy.orm import Session
from typing import Optional
from server.models import Resource
from server.repositories.base import BaseRepository

class ResourceRepository(BaseRepository[Resource]):
    def __init__(self, db: Session):
        super().__init__(Resource, db)

    def get_by_user_id(self, user_id: int) -> Optional[Resource]:
        return self.db.query(Resource).filter(Resource.user_id == user_id).first()
