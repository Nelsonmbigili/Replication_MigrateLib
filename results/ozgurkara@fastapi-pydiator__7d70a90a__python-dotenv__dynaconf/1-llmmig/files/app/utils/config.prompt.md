The following Python code currently uses the library "python-dotenv" version 1.0.1.
Migrate this code to use the library "dynaconf" version 3.2.10 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "python-dotenv" to "dynaconf".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "python-dotenv" and "dynaconf".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from starlette.config import Config

from dotenv import load_dotenv

load_dotenv()
config = Config(".env")

REDIS_HOST = config('REDIS_HOST', str, '0.0.0.0')
REDIS_PORT = config('REDIS_PORT', int, 6379)
REDIS_DB = config('REDIS_DB', int, 0)
REDIS_KEY_PREFIX = config('REDIS_KEY_PREFIX', str, 'fastapi_pydiator:')

DISTRIBUTED_CACHE_IS_ENABLED = config("DISTRIBUTED_CACHE_IS_ENABLED", bool, True)
CACHE_PIPELINE_IS_ENABLED = config("CACHE_PIPELINE_IS_ENABLED", bool, False)
LOG_PIPELINE_IS_ENABLED = config("LOG_PIPELINE_IS_ENABLED", bool, True)



```