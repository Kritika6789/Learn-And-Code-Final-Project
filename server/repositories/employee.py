from sqlalchemy.orm import Session
from typing import Optional
from server.models import Employee
from server.repositories.base import BaseRepository

class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: Session):
        super().__init__(Employee, db)

    def get_by_user_id(self, user_id: int) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.user_id == user_id).first()
