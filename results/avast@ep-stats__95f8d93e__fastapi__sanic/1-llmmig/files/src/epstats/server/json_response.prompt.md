The following Python code currently uses the library "fastapi" version 0.111.1.
Migrate this code to use the library "sanic" version 25.3.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "fastapi" to "sanic".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "fastapi" and "sanic".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import json as json
import typing

from fastapi.responses import JSONResponse


class DataScienceJsonResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # we need to use default json implementation and explicitly encode in utf-8 to
        # preserver `np.nan` and `np.inf` values.
        return json.dumps(content).encode("utf-8")

```