from threading import Thread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cherrypy


def render_template(template_name, **kwargs):
    """
    A simple template rendering function to replace Flask's render_template.
    It reads the template file and substitutes placeholders with provided values.
    """
    with open(template_name, 'r') as template_file:
        template_content = template_file.read()
    return template_content.format(**kwargs)


def send_async_email(to, subject, template, **kwargs):
    """
    Sends an email asynchronously using smtplib.
    """
    # Email configuration (replace with your SMTP server details)
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    smtp_username = 'your_username'
    smtp_password = 'your_password'
    from_email = 'your_email@example.com'

    # Create the email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to

    # Render the email body (text and HTML)
    text_body = render_template(template + '.txt', **kwargs)
    html_body = render_template(template + '.html', **kwargs)

    # Attach the text and HTML parts to the email
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to, msg.as_string())
    except Exception as e:
        cherrypy.log(f"Failed to send email: {e}")


def send_email(to, subject, template, **kwargs):
    """
    Starts a thread to send an email asynchronously.
    """
    thread = Thread(target=send_async_email, args=(to, subject, template), kwargs=kwargs)
    thread.start()
    return thread
