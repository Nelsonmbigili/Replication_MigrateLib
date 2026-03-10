### Explanation of Changes

To migrate the code from using Flask to FastAPI, the following changes were made:

1. **Import Statements**: The `flask` and `flask_mail` imports were replaced with FastAPI-compatible imports. FastAPI does not have a built-in mail sending feature, so we will continue to use the `flask_mail` library for sending emails.
  
2. **Application Context**: FastAPI does not use the same application context as Flask. Instead, we can directly use the `mail` object without needing to create an application context. 

3. **Threading**: The threading logic remains the same, as it is not specific to Flask or FastAPI.

4. **Rendering Templates**: FastAPI does not have a built-in template rendering system like Flask. If you want to render templates, you would typically use a separate templating engine like Jinja2. However, since the original code uses Flask's `render_template`, we will keep that part unchanged for the sake of this migration.

Here is the modified code:

```python
from threading import Thread

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from flask_mail import Message

from api.app import mail

# Initialize FastAPI app and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Assuming templates are in a 'templates' directory

def send_async_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.body = templates.get_template(template + '.txt').render(**kwargs)  # Using Jinja2 to render
    msg.html = templates.get_template(template + '.html').render(**kwargs)  # Using Jinja2 to render
    mail.send(msg)

def send_email(to, subject, template, **kwargs):  # pragma: no cover
    thread = Thread(target=send_async_email, args=(to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
```

### Note
- The `Jinja2Templates` is initialized to handle template rendering, assuming the templates are stored in a directory named "templates". Adjust the directory path as necessary based on your project structure.
- The `current_app` context is removed since FastAPI does not require it in the same way as Flask.