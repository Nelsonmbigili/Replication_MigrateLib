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
