### Explanation of Changes:
To migrate from `jinja2` to `mako`, the following changes were made:
1. **Template Syntax**: Mako uses `${}` for variable interpolation instead of `{{}}`. Loops and conditionals in Mako are written using `%` directives instead of `{% %}`.
2. **Whitespace Control**: Mako does not use `-` for whitespace control (e.g., `{%-` or `-%}`). Instead, whitespace control is handled by the template structure itself.
3. **Template Structure**: Mako requires explicit use of `%` for control structures like loops and conditionals, and these blocks must be properly closed with `%endfor`, `%endif`, etc.

Below is the modified code using the `mako` library:

### Modified Code:
```python
"""${name}.

Parameters
----------
% for p in params:
${p.argument} :% if p.annotation: ${p.annotation}% endif
    ${p.argument}
% endfor
% if return_type:
Returns
-------
${return_type}

% endif
"""
```