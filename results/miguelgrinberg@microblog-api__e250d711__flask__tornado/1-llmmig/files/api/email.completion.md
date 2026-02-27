### Explanation of Changes:
To migrate the code from Flask to Tornado, the following changes were made:
1. **Flask-Specific Imports**: Removed Flask-specific imports (`current_app`, `render_template`, and `Message`) and replaced them with Tornado equivalents or custom implementations.
2. **Email Sending**: Tornado does not have a built-in email-sending library like Flask-Mail. Instead, I used Python's `smtplib` and `email` libraries to send emails.
3. **Template Rendering**: Tornado uses its own template rendering system. I replaced `render_template` with Tornado's `tornado.template.Loader` for rendering `.html` and `.txt` templates.
4. **Application Context**: Tornado does not have an application context like Flask. I removed the `app.app_context()` block and adjusted the code accordingly.
5. **Threading**: Tornado supports asynchronous programming natively. I replaced the `Thread` with Tornado's `async def` and `await` for asynchronous email sending.

### Modified Code:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tornado.template import Loader
from tornado.ioloop import IOLoop


# Configure your email settings here
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_username"
SMTP_PASSWORD = "your_password"
FROM_EMAIL = "your_email@example.com"


async def send_async_email(to, subject, template, **kwargs):
    # Load templates using Tornado's template loader
    loader = Loader("templates")  # Assumes templates are in a "templates" directory
    text_body = loader.load(template + ".txt").generate(**kwargs).decode("utf-8")
    html_body = loader.load(template + ".html").generate(**kwargs).decode("utf-8")

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    # Attach plain text and HTML versions
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Send the email using smtplib
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")


def send_email(to, subject, template, **kwargs):
    # Schedule the async email sending in Tornado's event loop
    IOLoop.current().spawn_callback(send_async_email, to, subject, template, **kwargs)
```

### Key Notes:
1. **Email Configuration**: Replace `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `FROM_EMAIL` with your actual email server details.
2. **Template Directory**: Ensure that your `.txt` and `.html` templates are stored in a directory named `templates` (or adjust the `Loader` path accordingly).
3. **Asynchronous Execution**: Tornado's `IOLoop.current().spawn_callback` is used to schedule the `send_async_email` coroutine for execution without blocking the main thread.

This code is now fully migrated to use Tornado instead of Flask.