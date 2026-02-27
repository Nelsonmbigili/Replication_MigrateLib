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

from rattr.models.results.function import FunctionResults

if TYPE_CHECKING:
    from collections.abc import Iterator

    from rattr.versioning.typing import TypeAlias

FunctionName: TypeAlias = str


@attrs.mutable
class FileResults(MutableMapping[FunctionName, FunctionResults]):
    _function_results: dict[FunctionName, FunctionResults] = field(
        alias="function_results",
        factory=dict,
    )

    # ================================================================================ #
    # Mutable mapping abstract methods and mixin-overrides
    # ================================================================================ #

    def __getitem__(self, __key: FunctionName) -> FunctionResults:
        return self._function_results.__getitem__(__key)

    def __setitem__(
        self,
        __key: FunctionName,
        __value: FunctionResults,
    ) -> None:
        return self._function_results.__setitem__(__key, __value)

    def __delitem__(self, __key: FunctionName) -> None:
        return self._function_results.__delitem__(__key)

    def __iter__(self) -> Iterator[FunctionName]:
        return self._function_results.__iter__()

    def __len__(self) -> int:
        return self._function_results.__len__()

    def clear(self) -> None:
        # NOTE Better than derived implementation
        return self._function_results.clear()

```