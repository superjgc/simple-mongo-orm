import re


class classproperty(property):  # noqa
    """
    class Test:
        @classproperty
        def a(cls):
            return cls.__name__

    print(Test.a) -> Test
    print(Test().a) -> Test
    """

    def __get__(self, instance, owner):  # noqa
        return classmethod(self.fget).__get__(None, owner)()


def to_underline(key: str):
    return re.sub(r"[A-Z]", lambda match: f"_{match.group(0).lower()}", key).strip("_")
