from typing import Type, Optional, List


class MetaConstant(type):
    def __repr__(cls) -> str:
        parent = cls.mro()[1]
        if parent is object:
            return cls.__name__
        else:
            repr = f"{parent.__name__}.{cls.__name__}"
            if hasattr(cls, "value"):
                repr += f"('{cls.value}')"
            return repr


class Constant(metaclass=MetaConstant):
    def __new__(
        cls, val: Optional[str] = None, _dfs: Optional[List[Type]] = None
    ) -> "Constant":
        _dfs = [] if _dfs is None else _dfs
        _val: Optional[str] = getattr(cls, "value", None)
        if _val is None and val is None:
            raise NotImplementedError(
                f"Abstract {cls.__bases__[0].__name__} '{cls.__name__}' cannot be instantiated!"
            )
        elif _val is None:
            for child in cls.__subclasses__():
                try:
                    return child.__new__(child, val, _dfs=_dfs)
                except ValueError:
                    continue
            raise ValueError(
                f"'{val}' is not a valid {cls.__name__}. Expected {cls.__name__}s: {', '.join([repr(c.value) for c in _dfs])}"
            )
        elif val is None:
            return super(Constant, cls).__new__(cls)
        else:
            if _val == val:
                return super(Constant, cls).__new__(cls)
            _dfs.append(cls)
            raise ValueError(
                f"'{val}' cannot be validated as type {cls.__name__}. Expected '{_val}'"
            )

    def __init_subclass__(cls) -> None:
        setattr(type(cls), cls.__name__, cls)

    def __setattr__(self, name, value):
        del name, value  # pylance noqa
        raise NotImplementedError("Cannot update attribute/value of a Constant")

    def __repr__(self) -> str:
        return str(type(self))

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: "Constant") -> bool:
        return self.value == other.value
