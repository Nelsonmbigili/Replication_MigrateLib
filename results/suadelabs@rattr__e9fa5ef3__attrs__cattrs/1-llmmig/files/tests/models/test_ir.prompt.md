The following Python code currently uses the library "attrs" version 23.2.0.
Migrate this code to use the library "cattrs" version 23.2.3 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "attrs" to "cattrs".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "attrs" and "cattrs".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import pytest

from rattr.models.ir import FileIr, FunctionIr
from rattr.models.symbol import CallInterface, Func, Name, UserDefinedCallableSymbol

if TYPE_CHECKING:
    from rattr.models.context import Context
    from tests.shared import MakeRootContextFn


@pytest.fixture
def context_a(
    make_root_context: MakeRootContextFn,
) -> Context:
    return make_root_context([Name("hi")], include_root_symbols=True)


@pytest.fixture
def context_b(
    make_root_context: MakeRootContextFn,
) -> Context:
    return make_root_context([Name("not_hi")], include_root_symbols=True)


@pytest.fixture
def underlying_file_ir_a() -> dict[UserDefinedCallableSymbol, FunctionIr]:
    return {
        Func("fn", interface=CallInterface(args=("a",))): {
            "gets": {Name("thing.attr")},
            "sets": set(),
            "dels": set(),
            "calls": set(),
        }
    }


@pytest.fixture
def underlying_file_ir_b() -> dict[UserDefinedCallableSymbol, FunctionIr]:
    # Different attr accessed
    return {
        Func("fn", interface=CallInterface(args=("a",))): {
            "gets": {Name("thing.not_the_other_attr")},
            "sets": set(),
            "dels": set(),
            "calls": set(),
        }
    }


def test_equality_with_matching_context_and_matching_ir(
    context_a: Context,
    underlying_file_ir_a: dict[UserDefinedCallableSymbol, FunctionIr],
):
    lhs = FileIr(
        context=copy.deepcopy(context_a),
        file_ir=copy.deepcopy(underlying_file_ir_a),
    )
    rhs = FileIr(
        context=copy.deepcopy(context_a),
        file_ir=copy.deepcopy(underlying_file_ir_a),
    )
    assert lhs == rhs


def test_equality_with_matching_context_and_non_matching_ir(
    context_a: Context,
    underlying_file_ir_a: dict[UserDefinedCallableSymbol, FunctionIr],
    underlying_file_ir_b: dict[UserDefinedCallableSymbol, FunctionIr],
):
    lhs = FileIr(
        context=copy.deepcopy(context_a),
        file_ir=copy.deepcopy(underlying_file_ir_a),
    )
    rhs = FileIr(
        context=copy.deepcopy(context_a),
        file_ir=copy.deepcopy(underlying_file_ir_b),
    )
    assert lhs != rhs


def test_equality_with_non_matching_context_and_matching_ir(
    context_a: Context,
    context_b: Context,
    underlying_file_ir_a: dict[UserDefinedCallableSymbol, FunctionIr],
):
    lhs = FileIr(
        context=copy.deepcopy(context_a),
        file_ir=copy.deepcopy(underlying_file_ir_a),
    )
    rhs = FileIr(
        context=copy.deepcopy(context_b),
        file_ir=copy.deepcopy(underlying_file_ir_a),
    )
    assert lhs != rhs


def test_equality_with_non_matching_context_and_non_matching_ir(
    context_a: Context,
    context_b: Context,
    underlying_file_ir_a: dict[UserDefinedCallableSymbol, FunctionIr],
    underlying_file_ir_b: dict[UserDefinedCallableSymbol, FunctionIr],
):
    lhs = FileIr(
        context=copy.deepcopy(context_a),
        file_ir=copy.deepcopy(underlying_file_ir_a),
    )
    rhs = FileIr(
        context=copy.deepcopy(context_b),
        file_ir=copy.deepcopy(underlying_file_ir_b),
    )
    assert lhs != rhs

```