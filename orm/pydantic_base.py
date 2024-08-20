import datetime
import json
from typing import Any, Optional, Dict

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic._internal._generics import PydanticGenericMetadata
from pydantic._internal._model_construction import ModelMetaclass

from .column import Column


class Meta(ModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        __pydantic_generic_metadata__: PydanticGenericMetadata | None = None,
        __pydantic_reset_parent_namespace__: bool = True,
        _create_model_module: str | None = None,
        **kwargs: Any,
    ) -> type:
        cls = super().__new__(
            mcs,
            cls_name,
            bases,
            namespace,
            __pydantic_generic_metadata__=__pydantic_generic_metadata__,
            __pydantic_reset_parent_namespace__=__pydantic_reset_parent_namespace__,
            _create_model_module=_create_model_module,
            **kwargs,
        )
        # 主要是确保get attr不会报错
        fields: Dict[str, Any] = cls.model_fields
        for name, _ in namespace.get("__annotations__", {}).items():
            keys = [k for k in fields.keys() if k == name]
            if keys:
                # 注入Column
                setattr(cls, name, Column(keys[0]))
        return cls


class PydanticBase(BaseModel, metaclass=Meta):
    _extra_info: dict[str, Any] = PrivateAttr({})

    model_config = ConfigDict(
        json_encoders={
            datetime.datetime: (lambda obj: obj.strftime("%Y-%m-%d %H:%M:%S")),
            datetime.date: (lambda obj: obj.strftime("%Y-%m-%d")),
            datetime.timedelta: (
                lambda obj: f"{obj.seconds // 3600 + obj.days * 24}:"
                f"{(obj.seconds - obj.seconds // 3600 * 3600) // 60}:"
                f"{obj.seconds % 60}"
            ),
            ObjectId: str,
        },
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        # 将未在class定义的参数存储在_extra_info中
        self._extra_info = {k: v for k, v in data.items() if k not in self.model_fields}

    def __getattr__(self, item):
        try:
            # 先尝试获取class中的属性
            return super().__getattr__(item)
        except AttributeError as e:
            try:
                # 获取_extra_info中的属性（额外为定义字段信息）
                return self._extra_info[item]
            except KeyError:
                raise e

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        data = super().model_dump(*args, **kwargs)
        # 需要将_extra_info中的数据合并到返回的数据中
        data.update(self._extra_info)
        return data

    def model_dump_json(self, *, indent: Optional[int] = None, **kwargs) -> str:
        # 整合_extra_info到返回的数据中
        # todo 这块可尝试以用内置的json序列化方法
        data = self.model_dump(**kwargs)

        class CustomJsonEncoder(json.JSONEncoder):
            def default(_self, obj):  # noqa
                for _type, func in self.model_config.get("json_encoders", {}).items():
                    if isinstance(obj, _type):
                        return func(obj)
                return super().default(obj)

        return json.dumps(data, cls=CustomJsonEncoder, indent=indent)
