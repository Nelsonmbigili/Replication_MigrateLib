### Explanation of the Changes:
To migrate from "jinja2" to "mako", the following changes were made:
1. The syntax for templates in "jinja2" (e.g., `{{ name }}`) was replaced with the equivalent "mako" syntax (e.g., `${name}`).
2. The "mako" library uses `${}` for variable interpolation instead of `{{}}` in "jinja2".
3. No additional changes were made, as the template is simple and does not include advanced features.

### Modified Code:
```python
"""${name}."""

```