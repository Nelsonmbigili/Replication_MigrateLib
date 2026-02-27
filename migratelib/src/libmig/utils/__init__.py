from typing import TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


def update_dict_list(dict: dict[TKey, list[TValue]], key: TKey, values: list[TValue]):
    if key not in dict:
        dict[key] = []
    dict[key] += values


def safe_div(a: float, b: float, default=0) -> float:
    if b == 0:
        return default
    return a / b
