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
