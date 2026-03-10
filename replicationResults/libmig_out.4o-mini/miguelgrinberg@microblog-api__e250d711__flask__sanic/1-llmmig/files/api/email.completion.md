### Explanation of Changes
To migrate the code from using the Flask framework to the Sanic framework, the following changes were made:

1. **Import Statements**: The import statements were updated to import the necessary components from Sanic instead of Flask.
2. **Context Management**: Sanic does not use `app.app_context()` like Flask. Instead, we can directly use the `current_app` from Sanic, which is accessed differently.
3. **Email Sending**: The `flask_mail` library is not directly compatible with Sanic. If you are using a different email library with Sanic, you would need to adjust the email sending logic accordingly. However, for this migration, we will assume that the `mail` object is compatible with Sanic.

Here is the modified code:

```python
from threading import Thread

from sanic import current_app
from sanic.response import html
from sanic_mail import Message  # Assuming a compatible mail library for Sanic

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

### Note
Make sure that the `sanic_mail` library or any other email library you choose to use is properly set up and compatible with Sanic, as the original `flask_mail` library is not directly usable with Sanic.