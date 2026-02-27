The following Python code currently uses the library "flask" version 3.0.3.
Migrate this code to use the library "fastapi" version 0.115.12 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "flask" to "fastapi".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "flask" and "fastapi".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from api.app import mail


def send_async_email(app, to, subject, template, **kwargs):
    with app.app_context():  # pragma: no cover
        msg = Message(subject, recipients=[to])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)


def send_email(to, subject, template, **kwargs):  # pragma: no cover
    app = current_app._get_current_object()
    thread = Thread(target=send_async_email, args=(app, to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread

```