from _collections import defaultdict

import ast
from _ast import *


def callee_name(callee: ast.Call) -> str:
    func = callee.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    assert False, f"Unexpected callee type: {func}"
