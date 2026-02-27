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
"""Tests shared across multiple analysers."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import attrs
import pytest

from rattr.analyser.file import FileAnalyser
from rattr.models.context import compile_root_context
from rattr.models.symbol import Call, CallArguments, CallInterface, Func, Name
from tests.shared import match_output

if TYPE_CHECKING:
    from typing import Iterator

    from tests.shared import ParseFn, StateFn


@pytest.fixture(autouse=True)
def __set_current_file(state: StateFn) -> Iterator[None]:
    with state(current_file=Path(__file__)):
        yield


class TestAnnotations:
    def test_rattr_ignore(self, parse: ParseFn):
        # FunctionDef
        _ast = parse(
            """
            def a_func(arg):
                return arg.attr

            @rattr_ignore
            def another_func(arg):
                return arg.another_attr
            """
        )
        results = FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        a_func = Func(name="a_func", interface=CallInterface(args=("arg",)))
        a_func_async = attrs.evolve(a_func, is_async=True)

        expected = {
            a_func: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("arg.attr", "arg"),
                },
                "sets": set(),
            },
        }
        assert results.ir_as_dict() == expected

        # AsyncFunctionDef
        _ast = parse(
            """
            async def a_func(arg):
                return arg.attr

            @rattr_ignore
            async def another_func(arg):
                return arg.another_attr
            """
        )
        results = FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        expected = {
            a_func_async: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("arg.attr", "arg"),
                },
                "sets": set(),
            },
        }
        assert results.ir_as_dict() == expected

        # ClassDef
        # AsyncFunctionDef
        _ast = parse(
            """
            async def a_func(arg):
                return arg.attr

            @rattr_ignore
            class SomeClass:
                def __init__(self, a):
                    self.a = a
            """
        )
        results = FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        expected = {
            a_func_async: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("arg.attr", "arg"),
                },
                "sets": set(),
            },
        }
        assert results.ir_as_dict() == expected

    def test_rattr_results_for_basic_function(self, parse: ParseFn):
        # FunctionDef
        # Use incorrect results to show override is working
        _ast = parse(
            """
            def a_func(arg):
                return arg.attr

            @rattr_results(gets={"a", "b"})
            def another_func(arg):
                return arg.another_attr
            """
        )
        results = FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        a_func = Func(name="a_func", interface=CallInterface(args=("arg",)))
        another_func = Func(name="another_func", interface=CallInterface(args=("arg",)))

        expected = {
            a_func: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("arg.attr", "arg"),
                },
                "sets": set(),
            },
            another_func: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("a"),
                    Name("b"),
                },
                "sets": set(),
            },
        }

        assert results.ir_as_dict() == expected

    def test_rattr_results_for_basic_async_function(self, parse: ParseFn):
        # AsyncFunctionDef
        # Use incorrect results to show override is working
        _ast = parse(
            """
            async def a_func(arg):
                return arg.attr

            @rattr_results()
            async def another_func(arg):
                return arg.another_attr
            """
        )
        results = FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        a_func = Func(
            name="a_func",
            interface=CallInterface(args=("arg",)),
            is_async=True,
        )
        another_func = Func(
            name="another_func",
            interface=CallInterface(args=("arg",)),
            is_async=True,
        )

        expected = {
            a_func: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("arg.attr", "arg"),
                },
                "sets": set(),
            },
            another_func: {
                "calls": set(),
                "dels": set(),
                "gets": set(),
                "sets": set(),
            },
        }

        assert results.ir_as_dict() == expected

        # ClassDef
        # TODO When classes added

    def test_rattr_results_complex(self, parse: ParseFn):
        # FunctionDef
        # Use incorrect results to show override is working
        _ast = parse(
            """
            def a_func(arg):
                return arg.attr

            @rattr_results(
                gets={"a.attr", "*b.value"},
                calls=[
                    ("fn_a", (["a", "a.attr"], {"key": "b.key"})),
                    ("fn_b_with_brackets()", (["a", "a.attr"], {"key": "b.key"})),
                ]
            )
            def another_func(arg):
                return arg.another_attr
            """
        )
        results = FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        a_func = Func(name="a_func", interface=CallInterface(args=("arg",)))
        another_func = Func(name="another_func", interface=CallInterface(args=("arg",)))

        expected = {
            a_func: {
                "calls": set(),
                "dels": set(),
                "gets": {
                    Name("arg.attr", "arg"),
                },
                "sets": set(),
            },
            another_func: {
                "calls": {
                    Call(
                        "fn_a()",
                        args=CallArguments(
                            args=("a", "a.attr"),
                            kwargs={"key": "b.key"},
                        ),
                    ),
                    Call(
                        "fn_b_with_brackets()",
                        args=CallArguments(
                            args=("a", "a.attr"),
                            kwargs={"key": "b.key"},
                        ),
                    ),
                },
                "dels": set(),
                "gets": {
                    Name("a.attr", "a"),
                    Name("*b.value", "b"),
                },
                "sets": set(),
            },
        }

        assert results.ir_as_dict() == expected

    def test_rattr_results_missing_comma(
        self,
        parse: ParseFn,
        capfd: pytest.CaptureFixture[str],
    ):
        # FunctionDef
        # Use incorrect results to show override is working
        _ast = parse(
            r"""
            # NOTE The missing "," after the first line in "calls"
            @rattr_results(
                calls=[
                    ("func_one", (["a"], {"b": "c"}))
                    ("func_two", (["b"], {"b": "c"}))
                ]
            )
            def foo(arg):
                ...
            """
        )

        with pytest.raises(SystemExit):
            FileAnalyser(_ast, compile_root_context(_ast)).analyse()

        _, stderr = capfd.readouterr()
        assert match_output(
            stderr,
            [
                "unable to parse 'rattr_results', you are likely missing a comma in "
                "'calls'",
            ],
        )

```