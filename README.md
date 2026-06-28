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

print(div(10, 2).unwrap())                      # 5.0
print(div(10, 0).unwrap_or(-1))                 # -1
print(div(10, 2).map(lambda x: x * 2).unwrap()) # 10.0

# Option：要么有值，要么空
def find(lst, target):
    for v in lst:
        if v == target:
            return Option.Some(v)
    return Option.Nothing()

find([1, 2, 3], 2).map(lambda x: x * 10).unwrap_or(0)  # 20
```

## Result 接口

| 方法 | 说明 | 示例 |
|---|---|---|
| `is_ok()` / `is_err()` | 判别 | `div(4,2).is_ok()  # True` |
| `unwrap()` | 取成功值，失败抛 `ValueError` | `div(4,2).unwrap()  # 2.0` |
| `unwrap_err()` | 取失败值，成功抛 `ValueError` | `div(4,0).unwrap_err()  # 'divide by zero'` |
| `unwrap_or(default)` | 失败给默认值 | `div(4,0).unwrap_or(-1)  # -1` |
| `unwrap_or_else(f)` | 失败懒求值 | `div(4,0).unwrap_or_else(lambda e: 999)  # 999` |
| `expect(msg)` | 失败时自定义异常 | `div(4,0).expect("bad")` |
| `map(f: T -> U)` | 成功则映射 | `div(4,2).map(lambda x: x*2).unwrap()  # 4.0` |
| `map_err(f: E -> F)` | 失败则映射 | `div(4,0).map_err(str.upper).unwrap_or(0)  # 0` |
| `and_then(f: T -> Result[U,E])` | 扁平链式 | `div(10,2).and_then(lambda x: div(x,2)).unwrap()  # 2.5` |
| `or_else(f: E -> Result[T,E])` | 失败时补救 | `div(10,0).or_else(lambda e: Result.Success(0)).unwrap()  # 0` |

模式匹配（Python 3.10+）：

```python
match div(10, 0):
    case Success(v):
        print("ok", v)
    case Failure(e):
        print("err", e)   # err divide by zero
```

## Option 接口

| 方法 | 说明 | 示例 |
|---|---|---|
| `is_some` / `is_nothing` | 判别属性 | `Option.Some(7).is_some  # True` |
| `unwrap()` | 取值，空抛 `ValueError` | `Some(7).unwrap()  # 7` |
| `unwrap_or(default)` | 空给默认值 | `Nothing().unwrap_or(99)  # 99` |
| `unwrap_or_else(f)` | 懒求值 | `Nothing().unwrap_or_else(lambda: 99)  # 99` |
| `map(f)` | 有值则映射 | `Some(7).map(str).unwrap()  # '7'` |
| `map_or(default, f)` | map + unwrap_or | `Nothing().map_or(0, lambda x: x*2)  # 0` |
| `and_then(f)` | 扁平链 | `Some(5).and_then(lambda x: Some(x*2))  # Some(10)` |
| `filter(pred)` | 条件过滤 | `Some(7).filter(lambda x: x>10)  # Nothing` |
| `or_(optb)` / `or_else(f)` | 备选 | `Nothing() | Some(3)  # Some(3)` |
| `ok_or(err)` | 转 Result | `Some(5).ok_or("empty")  # 5` |
| `iter()` | 0/1 元素迭代器 | `list(Some(3).iter())  # [3]` |
| `__bool__` | 真值测试 | `if Some(3): ...` |
| `\|` 运算符 | `opt_a \| opt_b` | `Some(1) | Some(2)  # Some(1)` |

便捷构造：

```python
Option.From(None)       # Nothing()
Option.From(42)         # Some(42)
```

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
