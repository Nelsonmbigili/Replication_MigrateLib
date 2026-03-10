### Explanation of Changes
To migrate the code from using the Flask framework to the CherryPy framework, the following changes were made:

1. **Removal of Flask-specific Imports**: The imports related to Flask and Flask-Mail were removed since CherryPy does not use these libraries.
2. **Context Management**: CherryPy does not have an equivalent to Flask's application context. Therefore, the context management code was removed.
3. **Email Sending**: The email sending functionality needs to be adapted to use a different method, as CherryPy does not have a built-in mail sending feature like Flask-Mail. For this example, we will assume that a similar mail sending function is available in the CherryPy context.

The modified code below reflects these changes while maintaining the original structure and naming conventions.

### Modified Code
```python
from threading import Thread

import cherrypy

# Assuming a similar mail sending function is available in the CherryPy context
from api.app import mail


def send_async_email(to, subject, template, **kwargs):
    # Directly using the mail object without app context
    msg = mail.Message(subject, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


def send_email(to, subject, template, **kwargs):  # pragma: no cover
    thread = Thread(target=send_async_email, args=(to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
```

In this modified code, the `send_async_email` function no longer requires the `app` parameter, and the context management has been removed. The threading mechanism remains unchanged, ensuring that the email sending process is still asynchronous.