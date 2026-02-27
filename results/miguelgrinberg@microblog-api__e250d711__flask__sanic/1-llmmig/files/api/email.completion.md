### Explanation of Changes:
To migrate the code from Flask to Sanic, the following changes were made:
1. **Sanic App Context**: Flask's `app.app_context()` is replaced with Sanic's `app.ext.get_context()`. Sanic does not have a direct equivalent to Flask's `current_app`, so the app instance is passed explicitly.
2. **Email Sending**: Flask-Mail is replaced with a Sanic-compatible email library. Since Sanic does not have a built-in email library, you would need to use an external library like `sanic-mail` or any other email-sending library. For this example, I assume `sanic-mail` is used.
3. **Template Rendering**: Flask's `render_template` is replaced with Sanic's `jinja2` extension for template rendering (`app.ext.jinja.render`).
4. **Threading**: The threading logic remains the same, as it is independent of the web framework.

Below is the modified code:

---

### Modified Code:
```python
from threading import Thread

from sanic import Sanic
from sanic_ext import Extend
from sanic_mail import Mail, Message

from api.app import mail


def send_async_email(app, to, subject, template, **kwargs):
    async with app.ext.get_context():  # Sanic's equivalent of app context
        msg = Message(
            subject=subject,
            recipients=[to],
            body=app.ext.jinja.render(template + '.txt', **kwargs),
            html=app.ext.jinja.render(template + '.html', **kwargs)
        )
        await mail.send(msg)


def send_email(to, subject, template, **kwargs):  # pragma: no cover
    app = Sanic.get_app()  # Get the current Sanic app instance
    thread = Thread(target=send_async_email, args=(app, to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
```

---

### Notes:
1. **Sanic-Mail Setup**: Ensure that `sanic-mail` is properly configured in your Sanic app (`mail` object). For example:
   ```python
   app = Sanic("MyApp")
   Extend(app)  # Enable Sanic extensions
   mail = Mail(app)
   app.config.MAIL_SERVER = "smtp.example.com"
   app.config.MAIL_PORT = 587
   app.config.MAIL_USERNAME = "your_username"
   app.config.MAIL_PASSWORD = "your_password"
   app.config.MAIL_USE_TLS = True
   app.config.MAIL_USE_SSL = False
   ```
2. **Jinja2 Setup**: Sanic's `jinja2` extension must be enabled for template rendering. For example:
   ```python
   app.ext.jinja.add_environment_variable("TEMPLATES_DIR", "./templates")
   ```
3. **Async/Await**: Sanic is an asynchronous framework, so the `send_async_email` function is now an `async` function. However, threading is still used to offload the email-sending task.

Make sure to install the required libraries (`sanic`, `sanic-ext`, `sanic-mail`) in your environment.