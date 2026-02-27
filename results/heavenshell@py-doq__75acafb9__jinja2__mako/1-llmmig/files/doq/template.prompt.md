The following Python code currently uses the library "jinja2" version 3.1.3.
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
from jinja2 import (
    Environment,
    FileSystemLoader,
)


class Template:
    def __init__(self, paths):
        self.env = Environment(
            loader=FileSystemLoader(paths),
            autoescape=False,
            auto_reload=False,
        )

    def load(self, params, filename=None):
        filename = filename or 'def.txt'
        template = self.env.get_template(filename)
        return template.render(**params)

```