from threading import Thread
from fastapi import FastAPI
from jinja2 import Environment, FileSystemLoader
from aiosmtplib import send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize FastAPI app
app = FastAPI()

# Configure Jinja2 environment for template rendering
template_env = Environment(loader=FileSystemLoader("templates"))

# Email configuration (replace with your actual email settings)
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_username"
SMTP_PASSWORD = "your_password"
FROM_EMAIL = "your_email@example.com"


def render_template(template_name, **kwargs):
    """Render a template using Jinja2."""
    template = template_env.get_template(template_name)
    return template.render(**kwargs)


async def send_async_email(to, subject, template, **kwargs):
    """Send an email asynchronously."""
    # Render email body and HTML
    body = render_template(template + ".txt", **kwargs)
    html = render_template(template + ".html", **kwargs)

    # Create email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    # Attach plain text and HTML versions
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send email using aiosmtplib
    await send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        use_tls=True,
    )


def send_email(to, subject, template, **kwargs):
    """Send an email using a background thread."""
    thread = Thread(
        target=lambda: app.loop.run_until_complete(
            send_async_email(to, subject, template, **kwargs)
        )
    )
    thread.start()
    return thread
