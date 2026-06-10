from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from server.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class IRepository(Generic[ModelType]):
    """
    Interface for standard CRUD operations (Interface Segregation Principle).
    """
    def get(self, id: int) -> Optional[ModelType]:
        pass

    def get_all(self) -> List[ModelType]:
        pass

    def create(self, obj_in: dict) -> ModelType:
        pass

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        pass

    def delete(self, id: int) -> ModelType:
        pass

class BaseRepository(IRepository[ModelType]):
    """
    Concrete implementation of the Repository Pattern.
    (Single Responsibility Principle - only handles DB access for a specific model).
    """
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
