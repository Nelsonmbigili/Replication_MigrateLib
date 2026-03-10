### Explanation of Changes
To migrate the code from using the Flask framework to the Tornado framework, several key changes were made:

1. **Import Statements**: The `flask` and `flask_mail` imports were replaced with Tornado's equivalent functionality. Tornado does not have a built-in mail module like Flask-Mail, so we will need to use a different approach for sending emails.
  
2. **Application Context**: Tornado does not have an application context like Flask. Therefore, the context management using `app.app_context()` was removed.

3. **Threading**: The threading mechanism remains the same, but we ensure that the email sending function is compatible with Tornado's asynchronous nature.

4. **Email Sending**: Since Tornado does not have a built-in mail sending feature, you would typically use an external library (like `smtplib` or a third-party service) to send emails. For this example, we will assume a simple SMTP setup using `smtplib`.

Here is the modified code:

```python
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from tornado import gen

from api.app import mail  # Assuming mail is still relevant for SMTP settings

def send_async_email(to, subject, template, **kwargs):
    # Prepare the email content
    body = render_template(template + '.txt', **kwargs)
    html = render_template(template + '.html', **kwargs)

    # Create the email message
    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = mail.default_sender  # Assuming mail.default_sender is defined
    msg['To'] = to

    # Send the email
    with smtplib.SMTP(mail.smtp_server, mail.smtp_port) as server:
        server.starttls()  # If using TLS
        server.login(mail.username, mail.password)  # Assuming credentials are set
        server.sendmail(mail.default_sender, [to], msg.as_string())

def send_email(to, subject, template, **kwargs):  # pragma: no cover
    thread = Thread(target=send_async_email, args=(to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
```

### Notes:
- The `render_template` function is assumed to be available in the context of the Tornado application, similar to how it was in Flask.
- The SMTP settings (like `smtp_server`, `smtp_port`, `username`, and `password`) are assumed to be part of the `mail` object, which should be configured appropriately for sending emails.
- The email sending process is now handled using Python's built-in `smtplib` library, which is a common approach when using Tornado.