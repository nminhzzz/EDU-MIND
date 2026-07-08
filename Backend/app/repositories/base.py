from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.mysql import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Fetch a paginated list of records."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record and immediately commit the transaction.
        Use this when the caller does not need to batch this write with others.
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_no_commit(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Add a new record to the session without committing.
        The caller controls the transaction boundary — call db.commit() when ready.
        db.flush() is called so the PK is assigned and the object can be used
        in subsequent statements within the same transaction.
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.flush()
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update an existing record.
        Only the fields present in obj_in are written — unset fields are left
        unchanged.  Applies update_data directly with setattr to avoid the
        overhead of serialising the full ORM object via jsonable_encoder.
        """
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        )
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Delete a record by primary key. Returns the deleted object or None."""
        # Use Session.get() — the SQLAlchemy 2.x-compatible identity-map lookup.
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
