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

from typing import TYPE_CHECKING, TypedDict

import attrs

from rattr.models.ir import FileIr

if TYPE_CHECKING:
    from rattr.versioning.typing import TypeAlias


FileName: TypeAlias = str
ModuleName: TypeAlias = str

ImportIrs: TypeAlias = dict[ModuleName, FileIr]


class TargetIr(TypedDict):
    filename: FileName
    ir: FileIr


@attrs.frozen
class OutputIrs:
    import_irs: ImportIrs
    target_ir: TargetIr

```