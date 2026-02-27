The following Python code currently uses the library "jinja2" version 3.1.4.
Migrate this code to use the library "mako" version 1.3.10 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "jinja2" to "mako".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "jinja2" and "mako".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import time
from typing import Any, Optional, Text, Tuple
from jinja2 import Environment  # pip install jinja2

def kb(value:int) -> str:
    return str(value // 1024) + " KB"


def mb(value:int) -> str:
    return str(value // 1024 // 1024) + " MB"


def gb(value:int) -> str:
    return str(value // 1024 / 1024 // 1024) + " GB"


def uptime(boot_time:float) -> str:
    upt = time.time() - boot_time

    retval = ""
    days = int(upt / (60 * 60 * 24))

    if days != 0:
        retval += str(days) + " " + ("days" if days > 1 else "day") + ", "

    minutes = int(upt / 60)
    hours = int(minutes / 60)
    hours %= 24
    minutes %= 60

    if hours != 0:
        retval += str(hours) + ":" + (str(minutes) if minutes >= 10 else "0" + str(minutes))
    else:
        retval += str(minutes) + " min"

    return retval

def uptimesec(boot_time: float) -> int:
    upt = time.time() - boot_time
    return round(upt)


def register_filters() -> Environment:
    env = Environment()
    env.filters['KB'] = kb
    env.filters['MB'] = mb
    env.filters['GB'] = gb
    env.filters['uptime'] = uptime
    env.filters['uptimesec'] = uptimesec
    return env

class Formatter:
    '''
    '''
    env = register_filters()

    @classmethod
    def get_format(cls, path:str) -> Tuple[str, Optional[str]]:
        '''
        Tuple would be a better choice for typing
        '''
        i = path.find("{{")
        if i > 0:
            i = path.rfind("/", 0, i)
            if i > 0:
                return (path[0:i], path[i+1:])
        return (path, None)

    @classmethod
    def format(cls, f:str, value: Any) -> Text:
        return cls.env.from_string(f).render(
            value if isinstance(value, dict) else {"x": value})

```