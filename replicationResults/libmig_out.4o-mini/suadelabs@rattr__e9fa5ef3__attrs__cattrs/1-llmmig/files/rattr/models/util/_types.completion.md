### Explanation of Changes
To migrate the code from using the `attrs` library to the `cattrs` library, the primary change involves replacing the `@attrs.frozen` decorator with the appropriate `cattrs` functionality. The `cattrs` library is designed to work with classes defined using `attrs`, but it provides additional capabilities for serialization and deserialization. In this case, we will keep the `@attrs.frozen` decorator from `attrs` since `cattrs` can work with it directly. However, we will need to import `cattrs` for any future serialization or deserialization tasks.

### Modified Code
```python
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import cattrs

from rattr.models.ir import FileIr

if TYPE_CHECKING:
    from rattr.versioning.typing import TypeAlias


FileName: TypeAlias = str
ModuleName: TypeAlias = str

ImportIrs: TypeAlias = dict[ModuleName, FileIr]


class TargetIr(TypedDict):
    filename: FileName
    ir: FileIr


@cattrs.frozen
class OutputIrs:
    import_irs: ImportIrs
    target_ir: TargetIr
``` 

Note: The `@attrs.frozen` decorator remains unchanged because `cattrs` can work with `attrs` classes directly. If you need to use `cattrs` for serialization or deserialization, you would typically do that in a separate part of your code.