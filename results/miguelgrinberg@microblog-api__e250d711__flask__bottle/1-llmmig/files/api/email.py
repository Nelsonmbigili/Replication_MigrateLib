from threading import Thread
from bottle import template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_async_email(mail_config, to, subject, template_name, **kwargs):
    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = mail_config["MAIL_DEFAULT_SENDER"]
    msg["To"] = to

    # Render the email body (text and HTML)
    text_body = template(template_name + '.txt', **kwargs)
    html_body = template(template_name + '.html', **kwargs)

    # Attach the text and HTML parts to the email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Send the email using smtplib
    with smtplib.SMTP(mail_config["MAIL_SERVER"], mail_config["MAIL_PORT"]) as server:
        if mail_config.get("MAIL_USE_TLS"):
            server.starttls()
        if mail_config.get("MAIL_USERNAME") and mail_config.get("MAIL_PASSWORD"):
            server.login(mail_config["MAIL_USERNAME"], mail_config["MAIL_PASSWORD"])
        server.sendmail(mail_config["MAIL_DEFAULT_SENDER"], [to], msg.as_string())


def send_email(to, subject, template_name, **kwargs):  # pragma: no cover
    # Mail configuration (replace with your actual configuration)
    mail_config = {
        "MAIL_SERVER": "smtp.example.com",
        "MAIL_PORT": 587,
        "MAIL_USE_TLS": True,
        "MAIL_USERNAME": "your_username",
        "MAIL_PASSWORD": "your_password",
        "MAIL_DEFAULT_SENDER": "noreply@example.com",
    }

    # Start a thread to send the email asynchronously
    thread = Thread(target=send_async_email, args=(mail_config, to, subject, template_name), kwargs=kwargs)
    thread.start()
    return thread
