import logging
from typing import ClassVar, Optional, Union, Any, Iterator

import pymongo
from bson import ObjectId
from pydantic import Field, ConfigDict
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertOneResult
from typing_extensions import TypeVar

from .pydantic_base import PydanticBase
from utils import to_underline, classproperty

ModelType = TypeVar("ModelType")


class ModelBase(PydanticBase):
    id: Optional[Union[str, ObjectId]] = Field(None, alias="_id", description="@pk")

    database: ClassVar[Database] = None

    model_config = ConfigDict(
        alias_generator=lambda f: "_id" if f == "id" else f,
    )

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self._extra_info.pop("_id", None)

    @classmethod
    def init_db(
        cls,
        host: str = "127.0.0.1",
        port: int = 27017,
        user: str = "",
        password: str = "",
        database: str = "",
    ):
        if not database:
            raise RuntimeError("database is required")
        client = pymongo.MongoClient(
            f"mongodb://{user}:{password}@{host}:{port}", maxPoolSize=100
        )
        cls.database = getattr(client, database)

    @classproperty
    def __collection_name__(cls):  # noqa
        return to_underline(cls.__name__)

    @classproperty
    def collection(cls) -> Collection:  # noqa
        return getattr(cls.database, cls.__collection_name__)

    @staticmethod
    def _conditions(*args):
        conditions = {}
        for arg in args:
            conditions.update(arg[0])
        _id = conditions.pop("id", None)
        if _id:
            conditions["_id"] = ObjectId(str(_id))
        return conditions

    @classmethod
    def find_one(cls: ModelType, *args) -> Optional[ModelType]:
        logging.debug(
            f'find one: query collection "{cls.__collection_name__}" with conditions: {cls._conditions(args)}'
        )
        result = cls.collection.find_one(cls._conditions(args))
        return cls(**result) if result else None

    @classmethod
    def find(cls: ModelType, *args) -> Iterator[ModelType]:
        logging.debug(
            f'find: query collection "{cls.__collection_name__}" with conditions: {cls._conditions(args)}'
        )
        result = cls.collection.find(cls._conditions(args))
        if not result:
            return []
        for item in result:
            yield cls(**item)

    @classmethod
    def get(cls: ModelType, _id: Union[str, ObjectId]) -> Optional[ModelType]:
        result = cls.collection.find({"_id": ObjectId(str(_id))})
        return cls(**result[0]) if result else None

    def insert(self, **kwargs) -> InsertOneResult:
        data = self.model_dump()
        data.update(kwargs)
        data.pop("id", None)
        return self.collection.insert_one(data)
