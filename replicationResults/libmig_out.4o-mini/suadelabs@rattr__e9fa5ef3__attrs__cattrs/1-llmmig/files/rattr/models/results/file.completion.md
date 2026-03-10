### Explanation of Changes
To migrate the code from using the `attrs` library to the `cattrs` library, the following changes were made:

1. **Import Changes**: The import statement for `attrs` was replaced with `cattrs`. The `field` function is now imported from `cattrs` instead of `attrs`.
2. **Class Decorator**: The `@attrs.mutable` decorator was removed, as `cattrs` does not require a mutable decorator for defining mutable mappings.
3. **Field Definition**: The `field` function is still used to define the `_function_results` attribute, but it is now sourced from `cattrs`.

The overall structure and functionality of the code remain unchanged, adhering to the original coding style.

### Modified Code
```python
from __future__ import annotations

from collections.abc import MutableMapping
from typing import TYPE_CHECKING

import cattrs
from cattrs import field

from rattr.models.results.function import FunctionResults

if TYPE_CHECKING:
    from collections.abc import Iterator

    from rattr.versioning.typing import TypeAlias

FunctionName: TypeAlias = str


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