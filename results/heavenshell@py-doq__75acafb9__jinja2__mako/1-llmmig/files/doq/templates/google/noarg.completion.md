### Explanation of the Changes:
To migrate from "jinja2" to "mako", the following changes were made:
1. **Template Syntax**: The Jinja2 syntax `{{ variable }}` for variable interpolation was replaced with Mako's `${variable}` syntax.
2. **Template Engine**: Jinja2 templates are processed using the `jinja2` library, while Mako templates are processed using the `mako` library. However, since the provided code snippet is only a template string, no additional changes (e.g., rendering logic) are required in this specific case.

### Modified Code:
```python
"""${name}.
"""
```