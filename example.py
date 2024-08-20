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
