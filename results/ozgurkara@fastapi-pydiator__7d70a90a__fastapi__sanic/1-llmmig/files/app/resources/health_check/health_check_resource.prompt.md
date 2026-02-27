The following Python code currently uses the library "fastapi" version 0.109.1.
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
from fastapi import status, APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("",
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_200_OK: {
                    "model": str,
                    "content": {
                        "text/plain": {
                            "example": "OK"
                        }
                    }
                }
            },
            response_class=PlainTextResponse)
async def get():
    return "OK"

```