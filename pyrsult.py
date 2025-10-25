"""
这是一个让你能够在python里面使用类似于Rust的Result类型的库

by: fexcode| https://github.com/fexcode/
at: 2025-10-18
on: https://github.com/fexcode/pyrsult
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union, Any, Callable, Iterator

T = TypeVar("T")
E = TypeVar("E")


class Result(ABC, Generic[T, E]):
    """抽象基类：统一 Success / Failure 的公共接口"""

    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: Any) -> None:
        self._value: Any = value

    # --------------- 判别函数 ---------------
    @abstractmethod
    def is_ok(self) -> bool: ...
    @abstractmethod
    def is_err(self) -> bool: ...

    # --------------- 取值函数 ---------------
    @abstractmethod
    def unwrap(self) -> T: ...
    @abstractmethod
    def unwrap_err(self) -> E: ...
    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...
    @abstractmethod
    def expect(self, msg: str) -> T: ...
    @abstractmethod
    def unwarp_or_else(self, func: Callable[[E], T]) -> T: ...

    # --------------- 工厂函数 ---------------
    @staticmethod
    def Success(value: T) -> Result[T, Any]:  # type: ignore
        return Success(value)  # type: ignore

    @staticmethod
    def Failure(error: E) -> Result[Any, E]:  # type: ignore
        return Failure(error)  # type: ignore


class Success(Result[T, Any]):
    """成功分支"""

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> Any:
        raise ValueError("Called unwrap_err on an Ok value")

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwarp_or_else(self, func: Callable[[E], T]) -> T:
        return self._value

    def expect(self, msg: str) -> T:
        return self._value

    def __repr__(self) -> str:
        return f"Success({self._value!r})"


class Failure(Result[Any, E]):
    """失败分支"""

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise ValueError(f"Unwrap failed | {self._value}")

    def unwrap_err(self) -> E:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return default

    def unwarp_or_else(self, func: Callable[[E], T]) -> T:
        return func(self._value)

    def expect(self, msg: str) -> T:
        raise ValueError(msg)

    def __repr__(self) -> str:
        return f"Failure({self._value!r})"


# T = TypeVar("T")
U = TypeVar("U")
# E = TypeVar("E")


class Option(ABC, Generic[T]):
    """Option 类型，用于处理可能缺失的值。

    用法示例
    --------
    >>> Some(42).map(lambda x: x * 2).unwrap_or(0)
    84
    >>> Nothing().unwrap_or_else(lambda: 123)
    123
    >>> Some(7).filter(lambda x: x > 10).or_else(lambda: Some(99))
    Some(99)
    """

    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: Any) -> None:
        self._value: Any = value

    # region 原始抽象接口
    @abstractmethod
    def is_some(self) -> bool: ...
    @abstractmethod
    def is_nothing(self) -> bool: ...
    @property
    @abstractmethod
    def iam_sure_this_value_is_not_nothing(self) -> T: ...

    NN = iam_sure_this_value_is_not_nothing

    @property
    @abstractmethod
    def Sm(self) -> Some[T]: ...

    # endregion

    # region 高阶函数（Rust 风格）
    def map(self, f: Callable[[T], U]):
        """如果为 Some，则应用函数 f 并返回新的 Some；否则返回 Nothing。"""
        if self.is_some():
            return Some(f(self.NN))
        return Nothing()

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        """map + unwrap_or 的组合。"""
        return f(self.NN) if self.is_some() else default

    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U]) -> U:
        """延迟求值版本的 map_or。"""
        return f(self.NN) if self.is_some() else default()

    def unwrap_or(self, default: T) -> T:
        """取出值，若为 Nothing 则返回 default。"""
        return self.NN if self.is_some() else default

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        """延迟求值版本的 unwrap_or。"""
        return self.NN if self.is_some() else f()

    def filter(self, predicate: Callable[[T], bool]):
        """若满足谓词则保留，否则变为 Nothing。"""
        if self.is_some() and predicate(self.NN):
            return self
        return Nothing()

    def and_then(self, f: Callable[[T], Option[U]]):
        """Rust 中的 flat_map：Some(x) → f(x)；Nothing → Nothing。"""
        return f(self.NN) if self.is_some() else Nothing()

    def or_(self, optb: Option[T]) -> Option[T]:
        """self 优先，若为 Nothing 则取 optb。"""
        return self if self.is_some() else optb

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        """延迟求值版本的 or_。"""
        return self if self.is_some() else f()

    def ok_or(self, err: E) -> Union[T, E]:
        """快速转为“值或错误”风格。"""
        if self.is_some():
            return self.NN
        return err

    def iter(self) -> Iterator[T]:
        """生成 0 或 1 个元素的迭代器，方便 for 循环。"""
        if self.is_some():
            yield self.NN

    def __bool__(self) -> bool:
        """在 if 判断中直接当作布尔值使用。"""
        return self.is_some()

    def __ror__(self, other: Option[T]) -> Option[T]:
        """支持 | 运算符：opt_a | opt_b 等价于 opt_a.or_(opt_b)。"""
        return self.or_(other)

    # region 静态构造
    @staticmethod
    def Some(value: T) -> Option[T]:
        return Some(value)

    @staticmethod
    def Nothing() -> Nothing:
        return Nothing()

    @staticmethod
    def Auto(value: Union[T, None]):
        return Some(value=value) if value is not None else Nothing()


class Some(Option[T]):
    def is_some(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    @property
    def Sm(self) -> Some[T]:
        return self

    @property
    def iam_sure_this_value_is_not_nothing(self) -> T:
        return self._value

    NN = iam_sure_this_value_is_not_nothing

    def __repr__(self) -> str:
        return f"Some({self._value!r})"


class Nothing:
    def is_some(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    @property
    def Sm(self):
        raise ValueError("这个值是 Nothing")

    @property
    def iam_sure_this_value_is_not_nothing(self) -> Any:
        raise ValueError("这个值是 Nothing")

    NN = iam_sure_this_value_is_not_nothing

    def __repr__(self) -> str:
        return "Nothing"


# ------------------- 业务代码 -------------------
def foo(x: int) -> Result[int, str]:
    return Result.Success(x) if x > 0 else Result.Failure("x should be positive")


if __name__ == "__main__":
    ok = foo(5)
    print(ok.unwrap())  # -> 5
    print(ok.unwrap_or(0))  # -> 5

    err = foo(-5)
    print(err.unwrap_or(0))  # -> 0
    # err.expect("custom msg")  # => ValueError: custom msg

    # match 语法
    match foo(-1):
        case Success(value):
            print("Success|", value)
        case Failure(error):
            print("Failure|", error)

    # Option 类型
    def bar(x):
        return Option.Auto(x)

    print(bar(5).Sm)  # -> Some(5)
    # print(bar(None).iter)
