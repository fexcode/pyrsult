# PyRsult

> Python Rusty Result Library：在 Python 中使用 Rust 风格的 `Result` 和 `Option` 类型。

版本：0.4.0 | [GitHub](https://github.com/fexcode/pyrsult)

---

## 安装

```bash
pip install git+https://github.com/fexcode/pyrsult.git
```

## 快速上手

```python
from pyrsult import Result, Option

# Result：要么成功，要么失败
def div(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Result.Failure("divide by zero")
    return Result.Success(a / b)

r = div(10, 2)
print(r.unwrap())              # 5.0
print(r.map(lambda x: x * 2))  # Success(10.0)

# Option：要么有值，要么空
def find(lst, target):
    for v in lst:
        if v == target:
            return Option.Some(v)
    return Option.Nothing()

find([1, 2, 3], 2).map(lambda x: x * 10).unwrap_or(0)  # 20
```

---

## Result 详解

`Result[T, E]` 是一个泛型联合类型，有两个分支：

- `Success[T]` — 操作成功，携带值 `T`
- `Failure[E]` — 操作失败，携带错误 `E`

### 构造

```python
Result.Success(value)  # → Success(value)
Result.Failure(error)  # → Failure(error)
```

`Success` 和 `Failure` 也可直接用作构造器（也支持 `match` 模式匹配）。

### 判别

#### `is_ok() -> bool`

判断当前值是否是 `Success`。

```python
Result.Success(42).is_ok()  # True
Result.Failure("err").is_ok()  # False
```

#### `is_err() -> bool`

判断当前值是否是 `Failure`。

```python
Result.Failure("err").is_err()  # True
Result.Success(42).is_err()  # False
```

### 取值

#### `unwrap() -> T`

取出 `Success` 内部的值。如果当前是 `Failure`，则抛出 `ValueError`。

```python
Result.Success(42).unwrap()           # 42
Result.Failure("bad").unwrap()        # ValueError: Unwrap failed | bad
```

#### `unwrap_err() -> E`

取出 `Failure` 内部的错误值。如果当前是 `Success`，则抛出 `ValueError`。

```python
Result.Failure("bad").unwrap_err()    # 'bad'
Result.Success(42).unwrap_err()       # ValueError: Called unwrap_err on an Ok value
```

#### `unwrap_or(default: T) -> T`

取出 `Success` 内部的值；如果是 `Failure`，则返回 `default`。

```python
Result.Failure("bad").unwrap_or(0)    # 0
Result.Success(42).unwrap_or(0)       # 42
```

#### `unwrap_or_else(func: Callable[[E], T]) -> T`

取出 `Success` 内部的值；如果是 `Failure`，则将错误传入 `func` 并返回其结果（懒求值）。

```python
Result.Failure("bad").unwrap_or_else(lambda e: len(e))  # 3
Result.Success(42).unwrap_or_else(lambda e: 0)           # 42
```

#### `expect(msg: str) -> T`

取出 `Success` 内部的值；如果是 `Failure`，则抛出 `ValueError`，异常消息为 `msg`。

```python
Result.Success(42).expect("custom")     # 42
Result.Failure("bad").expect("custom")  # ValueError: custom
```

### 变换

#### `map(func: Callable[[T], U]) -> Result[U, E]`

如果当前是 `Success`，对其内部值应用 `func` 并返回新的 `Success`；`Failure` 保持不变。

```python
Result.Success(10).map(lambda x: x * 2)  # Success(20)
Result.Failure("bad").map(lambda x: x)   # Failure('bad')
```

#### `map_err(func: Callable[[E], F]) -> Result[T, F]`

如果当前是 `Failure`，对其内部错误应用 `func` 并返回新的 `Failure`；`Success` 保持不变。

```python
Result.Failure("bad").map_err(str.upper)  # Failure('BAD')
Result.Success(42).map_err(str.upper)     # Success(42)
```

### 链式

#### `and_then(func: Callable[[T], Result[U, E]]) -> Result[U, E]`

如果当前是 `Success`，则将内部值传入 `func`（`func` 必须返回 `Result`），实现扁平化链式调用。类似 Rust 的 `and_then` / `flat_map`。`Failure` 保持不变。

```python
def safe_div(x: float) -> Result[float, str]:
    return Result.Failure("zero") if x == 0 else Result.Success(10 / x)

Result.Success(2.0).and_then(safe_div)   # Success(5.0)
Result.Success(0.0).and_then(safe_div)   # Failure('zero')
Result.Failure("err").and_then(safe_div) # Failure('err')
```

#### `or_else(func: Callable[[E], Result[T, F]]) -> Result[T, F]`

如果当前是 `Failure`，则将错误传入 `func` 进行补救；`Success` 保持不变。

```python
def补救(e: str) -> Result[int, str]:
    return Result.Success(42)

Result.Failure("bad").or_else(补救)      # Success(42)
Result.Success(10).or_else(补救)         # Success(10)
```

### 模式匹配

Python 3.10+ 支持直接对 `Result` 进行 `match`：

```python
match div(10, 0):
    case Success(v):
        print("ok", v)
    case Failure(e):
        print("err", e)   # err divide by zero
```

---

## Option 详解

`Option[T]` 用于表示一个值可能存在也可能不存在，有两个分支：

- `Some[T]` — 值存在
- `Nothing` — 值为空

### 构造

```python
Option.Some(value)   # → Some(value)
Option.Nothing()     # → Nothing
Option.From(value)   # value 不为 None → Some(value)，否则 → Nothing()
```

`Some` 和 `Nothing` 也可直接使用。

### 判别

#### `is_some: bool`（属性）

判断是否为 `Some`。

```python
Option.Some(42).is_some       # True
Option.Nothing().is_some      # False
```

#### `is_nothing: bool`（属性）

判断是否为 `Nothing`。

```python
Option.Nothing().is_nothing   # True
Option.Some(42).is_nothing    # False
```

### 取值

#### `unwrap() -> T`

取出 `Some` 内部的值。如果为 `Nothing` 则抛出 `ValueError`。

```python
Option.Some(42).unwrap()      # 42
Option.Nothing().unwrap()     # ValueError: 这个值是 Nothing
```

#### `unwrap_or(default: T) -> T`

取出 `Some` 内部的值；`Nothing` 时返回 `default`。

```python
Option.Nothing().unwrap_or(0)  # 0
Option.Some(42).unwrap_or(0)   # 42
```

#### `unwrap_or_else(func: Callable[[], T]) -> T`

取出 `Some` 内部的值；`Nothing` 时调用 `func` 并返回其结果（懒求值）。

```python
Option.Nothing().unwrap_or_else(lambda: 99)  # 99
Option.Some(42).unwrap_or_else(lambda: 99)   # 42
```

### 变换

#### `map(func: Callable[[T], U]) -> Option[U]`

如果为 `Some`，对内部值应用 `func` 并返回新的 `Some`；`Nothing` 保持不变。

```python
Option.Some(7).map(lambda x: x * 2)   # Some(14)
Option.Nothing().map(lambda x: x)     # Nothing
```

#### `map_or(default: U, func: Callable[[T], U]) -> U`

`map` + `unwrap_or` 的组合：`Some` 时应用 `func`，`Nothing` 时返回 `default`。

```python
Option.Some(7).map_or(0, lambda x: x * 2)   # 14
Option.Nothing().map_or(0, lambda x: x * 2)  # 0
```

#### `map_or_else(default: Callable[[], U], func: Callable[[T], U]) -> U`

`map` + `unwrap_or_else` 的组合，两个参数均为懒求值。

```python
Option.Some(7).map_or_else(lambda: 0, lambda x: x * 2)   # 14
Option.Nothing().map_or_else(lambda: 0, lambda x: x * 2)  # 0
```

### 链式

#### `and_then(func: Callable[[T], Option[U]]) -> Option[U]`

如果为 `Some`，将内部值传入 `func`（`func` 必须返回 `Option`），实现扁平化链式调用。类似 Rust 的 `and_then`。

```python
def parse_int(s: str) -> Option[int]:
    try:
        return Option.Some(int(s))
    except ValueError:
        return Option.Nothing()

Option.Some("42").and_then(parse_int)  # Some(42)
Option.Some("abc").and_then(parse_int) # Nothing
Option.Nothing().and_then(parse_int)   # Nothing
```

#### `filter(predicate: Callable[[T], bool]) -> Option[T]`

如果为 `Some` 且满足 `predicate`，则保留；否则变为 `Nothing`。

```python
Option.Some(7).filter(lambda x: x > 5)   # Some(7)
Option.Some(3).filter(lambda x: x > 5)   # Nothing
Option.Nothing().filter(lambda x: x > 5) # Nothing
```

### 备选

#### `or_(optb: Option[T]) -> Option[T]`

当前为 `Some` 时返回自身，否则返回 `optb`。

```python
Option.Some(1).or_(Option.Some(2))   # Some(1)
Option.Nothing().or_(Option.Some(2)) # Some(2)
```

#### `or_else(func: Callable[[], Option[T]]) -> Option[T]`

当前为 `Some` 时返回自身，否则调用 `func` 并返回其结果（懒求值）。

```python
Option.Nothing().or_else(lambda: Option.Some(99))  # Some(99)
Option.Some(1).or_else(lambda: Option.Some(99))    # Some(1)
```

### 类型转换

#### `ok_or(err: E) -> Union[T, E]`

将 `Option` 转为"值或错误"风格：`Some(v)` → `v`，`Nothing` → `err`。

```python
Option.Some(5).ok_or("empty")   # 5
Option.Nothing().ok_or("empty") # 'empty'
```

### 迭代

#### `iter() -> Iterator[T]`

返回包含 0 或 1 个元素的迭代器，方便 `for` 循环。

```python
for v in Option.Some(42).iter():
    print(v)  # 42

list(Option.Some(3).iter())   # [3]
list(Option.Nothing().iter()) # []
```

### 运算符

#### `__bool__`

`Option` 可直接用于布尔上下文。

```python
if Option.Some(42):
    print("有值")  # 输出：有值

bool(Option.Nothing())  # False
bool(Option.Some(42))   # True
```

#### `|` 运算符

`a | b` 等价于 `a.or_(b)`，取第一个非空值。

```python
Option.Nothing() | Option.Some(3)   # Some(3)
Option.Some(1) | Option.Some(2)     # Some(1)
```

### 快捷属性

#### `Sm -> Some[T]`

当确定当前值一定是 `Some` 时，直接获取 `Some` 包装（而非内部值）。若实际为 `Nothing` 则抛出 `ValueError`。

```python
Option.Some(5).Sm  # Some(5)
```

#### `NN -> T`

`iam_sure_this_value_is_not_nothing` 的别名。当确定当前值一定不是 `Nothing` 时，直接取出内部值。若实际为 `Nothing` 则抛出 `ValueError`。用法同 `unwrap()` 但不抛 `ValueError` 的包装异常。

```python
Option.Some(5).NN  # 5
```

---

## 实战：读取配置

```python
import os
from pyrsult import Result, Option

def env_int(key: str) -> Result[int, str]:
    val = os.getenv(key)
    return (
        Option.From(val)
        .map(int)
        .ok_or(f"{key} not a valid int")
    )

port = env_int("PORT").unwrap_or(8080)
```

---

欢迎 PR & Issue！
