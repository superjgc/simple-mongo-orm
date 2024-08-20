# simple-mongo-orm
A simple ORM for MongoDB in Python.

1. 使用pymongo操作数据库
2. 使用pydantic定义数据格式
3. 可查询出未定义的字段

## 使用方法
example.py ->
```python
from orm.model_base import ModelBase


class Person(ModelBase):
    name: str
    age: int = 18
    # weight: str  隐藏字段


if __name__ == "__main__":
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    ModelBase.init_db(
        host="127.0.0.1", port=27017, user="mongo", password="mongo", database="test"
    )

    Person.collection.drop()

    # 标准（对象）插入，name和age是Person定义的字段
    tom = Person(name="Tom", age=20).insert()
    # 此处插入额外字段weight，两种方式，1在初始化时，2在insert方法中
    john = Person(name="John", age=18, weight=70).insert()
    peter = Person(name="Peter", age=25).insert(weight=65)
    print(f"insert tom: {tom.inserted_id}")

    # 根据id唯一查询
    print(f"get tom: {Person.get(tom.inserted_id).model_dump()}")

    # 条件查询，在父类PydanticBase中可看到每个字段都是Column对象，该对象重写了魔法方法
    print(f'condition query: {Person.name == "John"}')
    for p in Person.find(Person.name == "John"):
        print(f"\tdict: {p.model_dump()}")
    print(f"condition query: {Person.age >= 20}")
    for p in Person.find(Person.age >= 20):
        print(f"\tdict: {p.model_dump()}")
        print(f"\tjson: {p.model_dump_json()}")
```
输出 ->
```shell
insert tom: 66c3f33ea0304d60cbd519ed
get tom: {'id': ObjectId('66c3f33ea0304d60cbd519ed'), 'name': 'Tom', 'age': 20}
condition query: {'name': 'John'}
        dict: {'id': ObjectId('66c3f33ea0304d60cbd519ee'), 'name': 'John', 'age': 18, 'weight': 70}
condition query: {'age': {'$gte': 20}}
        dict: {'id': ObjectId('66c3f33ea0304d60cbd519ed'), 'name': 'Tom', 'age': 20}
        json: {"id": "66c3f33ea0304d60cbd519ed", "name": "Tom", "age": 20}
        dict: {'id': ObjectId('66c3f33ea0304d60cbd519ef'), 'name': 'Peter', 'age': 25, 'weight': 65}
        json: {"id": "66c3f33ea0304d60cbd519ef", "name": "Peter", "age": 25, "weight": 65}
```

## 模块说明
1. orm.pydantic_base.PydanticBase
    - 将数据字段转化为Column对象注入cls中
    - 将为定义的字段存储在私有变量中
    - 输出dict时将未定义字段也输出
2. orm.model_base.ModelBase
    - 继承PydanticBase
    - 定义了mongo内置id的转化方法
    - 定义了collection与类名关系
    - 定义了查询、插入等方法，**如果有需要自己实现额外的操作**
3. orm.column.Column
    - 重写了魔法方法，用于查询时的比较
