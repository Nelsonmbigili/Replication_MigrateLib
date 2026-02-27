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

from collections.abc import MutableMapping
from typing import TYPE_CHECKING

import attrs
from attrs import field

from rattr.ast.types import Identifier
from rattr.models.symbol import Symbol

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, KeysView, ValuesView


@attrs.mutable
class SymbolTable(MutableMapping[Identifier, Symbol]):
    _symbols: dict[Identifier, Symbol] = field(init=False, factory=dict)

    @property
    def names(self) -> KeysView[Identifier]:
        return self._symbols.keys()

    @property
    def symbols(self) -> ValuesView[Symbol]:
        return self._symbols.values()

    def add(self, symbol_or_symbols: Symbol | Iterable[Symbol]) -> None:
        """Add the given symbol(s) to the symbol table."""
        if isinstance(symbol_or_symbols, Symbol):
            symbols = [symbol_or_symbols]
        else:
            symbols = symbol_or_symbols

        for symbol in symbols:
            self[symbol.id] = symbol

    def remove(
        self,
        target_or_targets: Identifier | Symbol | Iterable[Identifier | Symbol],
    ) -> None:
        """Remove the given target(s) from the symbol table."""
        if isinstance(target_or_targets, (Identifier, Symbol)):
            targets = [target_or_targets]
        else:
            targets = target_or_targets

        for t in targets:
            del self[t if isinstance(t, Identifier) else t.id]

    def pop(self, target: Identifier | Symbol) -> Symbol | None:
        """Return and remove the given target, returns `None` if absent."""
        id = target.id if isinstance(target, Symbol) else target

        if id not in self:
            return

        symbol = self[id]
        del self[id]
        return symbol

    # ================================================================================ #
    # Mutable mapping abstract methods and mixin-overrides
    # ================================================================================ #

    def __getitem__(self, __key: Identifier) -> Symbol:
        return self._symbols.__getitem__(__key)

    def __setitem__(self, __key: Identifier, __value: Symbol) -> None:
        return self._symbols.__setitem__(__key, __value)

    def __delitem__(self, __key: Identifier) -> None:
        return self._symbols.__delitem__(__key)

    def __iter__(self) -> Iterator[Identifier]:
        return self._symbols.__iter__()

    def __len__(self) -> int:
        return self._symbols.__len__()

    def clear(self) -> None:
        # Faster than MutableMapping's default clear implementation
        return self._symbols.clear()

```