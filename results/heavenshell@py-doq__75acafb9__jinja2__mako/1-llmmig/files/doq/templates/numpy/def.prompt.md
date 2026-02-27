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
"""{{ name }}.

Parameters
----------
{% for p in params -%}
{{ p.argument }} :{% if p.annotation %} {{ p.annotation }}{% endif %}
    {{ p.argument }}
{% endfor %}
{%- if return_type %}
Returns
-------
{{ return_type }}

{% endif -%}
"""

```