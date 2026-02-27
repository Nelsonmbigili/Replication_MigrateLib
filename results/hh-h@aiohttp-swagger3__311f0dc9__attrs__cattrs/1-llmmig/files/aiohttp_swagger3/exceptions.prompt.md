The following Python code currently uses the library "attrs" version 25.3.0.
Migrate this code to use the library "cattrs" version 24.1.3 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "attrs" to "cattrs".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "attrs" and "cattrs".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from typing import Dict, Union

import attr


@attr.attrs(slots=True, auto_attribs=True)
class ValidatorError(Exception):
    error: Union[str, Dict]


class DiscriminatorValidationError(Exception):
    pass

```