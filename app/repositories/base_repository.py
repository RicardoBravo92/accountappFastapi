from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository providing generic CRUD operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelType | None:
        """Get record by ID."""
        return db.execute(
            select(self.model).where(self.model.id == id)
        ).scalars().first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        return db.execute(
            select(self.model).offset(skip).limit(limit)
        ).scalars().all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """Delete record by ID."""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
