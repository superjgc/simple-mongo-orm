from typing import Any


class Column:
    """
    主要为重写__eq__等方法为mongo识别的查询条件
    """
    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return self.key

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: Any):
        return {self.key: other}

    def __ne__(self, other: Any):
        return {self.key: {"$ne": other}}

    def __lt__(self, other: Any):
        return {self.key: {"$lt": other}}

    def __le__(self, other: Any):
        return {self.key: {"$lte": other}}

    def __gt__(self, other: Any):
        return {self.key: {"$gt": other}}

    def __ge__(self, other: Any):
        return {self.key: {"$gte": other}}


if __name__ == '__main__':
    print(Column("name") == "Tom")  # {'name': 'Tom'}
    print(Column("age") >= 100)     # {'age': {'$gte': 100}}
