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

from typing import TYPE_CHECKING

import attrs
from attrs import field

from rattr.analyser.util import get_file_hash
from rattr.models.results import FileResults
from rattr.models.symbol import Import
from rattr.models.symbol._util import PYTHON_BUILTINS_LOCATION
from rattr.module_locator.util import is_in_import_blacklist

if TYPE_CHECKING:
    from rattr.analyser.types import ImportIrs
    from rattr.models.ir import FileIr


def make_cacheable_results(
    results: FileResults,
    target_ir: FileIr,
    import_irs: ImportIrs,
) -> CacheableResults:
    return CacheableResults(
        filepath=target_ir.context.file,
        filehash=get_file_hash(target_ir.context.file),
        imports=make_cacheable_import_info(target_ir, import_irs),
        results=results,
    )


def make_cacheable_import_info(
    target_ir: FileIr,
    import_irs: ImportIrs,
) -> list[CacheableImportInfo]:
    contexts = (
        target_ir.context,
        *(import_.context for import_ in import_irs.values()),
    )

    return sorted(
        {
            CacheableImportInfo.from_file(symbol.module_spec.origin)
            for context in contexts
            for symbol in context.symbol_table.symbols
            if isinstance(symbol, Import)
            if symbol.module_name is not None
            if not is_in_import_blacklist(symbol.module_name)
            if symbol.module_spec is not None
            if symbol.module_spec.origin is not None
            if symbol.module_spec.origin != PYTHON_BUILTINS_LOCATION
        },
        key=lambda info: info.filepath,
    )


@attrs.frozen
class CacheableImportInfo:
    filepath: str = field(converter=str)
    filehash: str

    @classmethod
    def from_file(cls, filepath: str) -> CacheableImportInfo:
        return CacheableImportInfo(filepath=filepath, filehash=get_file_hash(filepath))


@attrs.frozen
class CacheableResults:
    filepath: str = field(converter=str)
    filehash: str
    imports: list[CacheableImportInfo]
    results: FileResults

```