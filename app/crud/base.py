from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Базовый класс CRUD-операций.
        :param model: SQLAlchemy модель
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Получить объект по ID.
        """
        return db.query(self.model).get(id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Получить список объектов с поддержкой пагинации.
        :param skip: Количество записей для пропуска
        :param limit: Количество записей для возврата
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        Создать новый объект в базе данных.
        :param obj_in: Pydantic-схема с данными для создания
        """
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """
        Обновить существующий объект в базе данных.
        :param db_obj: Существующий SQLAlchemy-объект
        :param obj_in: Pydantic-схема с новыми данными
        """
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Удалить объект по ID.
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def filter_by(self, db: Session, **kwargs) -> List[ModelType]:
        """
        Получить список объектов по фильтрам (filter_by).
        :param kwargs: поля модели и их значения
        """
        return db.query(self.model).filter_by(**kwargs).all()

    def exists(self, db: Session, **kwargs) -> bool:
        """
        Проверить, существует ли объект по заданным условиям.
        :param kwargs: поля модели и их значения
        """
        return db.query(self.model).filter_by(**kwargs).first() is not None
