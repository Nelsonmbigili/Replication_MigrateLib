### Explanation of Changes:
To migrate from "jinja2" to "mako", the following changes were made:
1. The syntax for templates in "jinja2" (e.g., `{{ variable }}`) was replaced with the "mako" equivalent `${variable}`.
2. The "mako" template syntax uses `${}` for variable interpolation instead of `{{}}`.

Below is the modified code using "mako":

### Modified Code:
```python
"""${name}.
"""
```