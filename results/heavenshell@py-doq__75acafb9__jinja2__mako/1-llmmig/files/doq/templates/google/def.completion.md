### Explanation of Changes:
To migrate from `jinja2` to `mako`, the following changes were made:
1. **Template Syntax**: Mako uses `${}` for variable interpolation instead of `{{}}`. Additionally, Mako uses `%` for control structures like loops and conditionals, instead of `{% %}` in Jinja2.
2. **Whitespace Control**: Mako does not have built-in whitespace control like Jinja2's `-` suffix. Instead, you can use explicit formatting or adjust the template structure to control whitespace.
3. **Template Rendering**: Mako templates are rendered using the `Template` class from `mako.template`, and rendering is done via the `render()` method.

Below is the modified code using Mako:

### Modified Code:
```python
"""${name}.

Args:
% for p in params:
    ${p.argument}${' (' + p.annotation + '): ' + p.argument if p.annotation else ':'}
% endfor
% if return_type:
Returns:
    ${return_type}:
% endif
"""
```

### Key Notes:
- `${name}` replaces `{{ name }}` for variable interpolation.
- `% for` and `% endfor` replace `{% for %}` and `{% endfor %}` for loops.
- `% if` and `% endif` replace `{% if %}` and `{% endif %}` for conditionals.
- The inline conditional for `p.annotation` is rewritten using Python string concatenation within `${}`.
- Whitespace control is handled by the structure of the template itself, as Mako does not have a direct equivalent to Jinja2's `-` for trimming whitespace.